"""
Advanced Preprocessing and NER Pipeline for Geo-Compliance Classification

This module implements the first stage of the feature flow:
1. Pre-processing and tokenization
2. NER and Regex searches for clear-cut geotagging cases  
3. High-confidence (95%) detection for obvious cases
"""

import re
import logging
from typing import List, Dict, Tuple, Set, Optional, Any
from dataclasses import dataclass
from src.backend.knowledge.glossary import get_glossary, LocationMapping, AgeMapping, TerminologyMapping

# HuggingFace imports
try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    import torch
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    AutoTokenizer = None
    AutoModelForTokenClassification = None
    pipeline = None
    torch = None

logger = logging.getLogger(__name__)

@dataclass
class EntityMatch:
    """Represents a detected entity with confidence scoring"""
    text: str
    entity_type: str  # "LOCATION", "AGE", "TERMINOLOGY" 
    start_pos: int
    end_pos: int
    confidence: float
    standardized_form: str
    source: str  # "regex", "ner", "glossary"
    additional_info: Dict[str, Any] = None

@dataclass
class PreprocessingResult:
    """Results from the preprocessing pipeline"""
    original_text: str
    cleaned_text: str
    tokens: List[str]
    entities: List[EntityMatch]
    clear_cut_classification: Optional[bool]  # True/False for 95% confidence cases, None for uncertain
    confidence_score: float
    needs_further_analysis: bool

class GeoCompliancePreprocessor:
    """
    Advanced preprocessing pipeline for geo-compliance feature classification.
    Implements tokenization, NER, and regex-based detection for high-confidence cases.
    """
    
    def __init__(self):
        self.glossary = get_glossary()
        self.ner_pipeline = None
        self._load_huggingface_ner()
        self._compile_regex_patterns()
        
        # High confidence thresholds
        self.HIGH_CONFIDENCE_THRESHOLD = 0.95
        self.CLEAR_CUT_THRESHOLD = 0.95
        
    def _load_huggingface_ner(self):
        """Load HuggingFace NER model with error handling"""
        if not HUGGINGFACE_AVAILABLE:
            logger.warning("HuggingFace transformers not available, NER will be disabled")
            self.ner_pipeline = None
            return
            
        try:
            # Use a lightweight but effective NER model
            model_preferences = [
                "dslim/bert-base-NER",  # Lightweight and effective
                "dbmdz/bert-large-cased-finetuned-conll03-english",  # High quality but larger
                "microsoft/DialoGPT-medium"  # Fallback
            ]
            
            for model_name in model_preferences:
                try:
                    logger.info(f"Loading HuggingFace NER model: {model_name}")
                    
                    # Set device
                    device = 0 if torch and torch.cuda.is_available() else -1
                    
                    self.ner_pipeline = pipeline(
                        "ner", 
                        model=model_name,
                        tokenizer=model_name,
                        aggregation_strategy="simple",  # Group subword tokens
                        device=device
                    )
                    
                    logger.info(f"Successfully loaded HuggingFace NER model: {model_name}")
                    return
                    
                except Exception as model_error:
                    logger.warning(f"Failed to load {model_name}: {model_error}")
                    continue
            
            # If all models fail, disable NER
            logger.warning("All HuggingFace NER models failed to load, NER will be disabled")
            self.ner_pipeline = None
                
        except Exception as e:
            logger.error(f"Failed to load HuggingFace NER model: {e}")
            self.ner_pipeline = None
    
    def _compile_regex_patterns(self):
        """Compile regex patterns for high-confidence detection"""
        
        # Get all variants from glossary for pattern building
        location_variants = self.glossary.get_all_location_variants()
        age_variants = self.glossary.get_all_age_variants()
        terminology_variants = self.glossary.get_all_terminology_variants()
        
        # LOCATION PATTERNS (Clear geographic indicators)
        location_pattern_parts = []
        
        # Escape special regex characters and sort by length (longest first)
        escaped_locations = [re.escape(loc) for loc in location_variants]
        escaped_locations.sort(key=len, reverse=True)
        
        # Country/region patterns
        location_pattern_parts.extend([
            r'\b(?:in|for|within|from|to)\s+(' + '|'.join(escaped_locations[:50]) + r')\b',  # "in US", "for EU"
            r'\b(' + '|'.join(escaped_locations[:50]) + r')\s+(?:users?|residents?|citizens?|law|regulation|compliance)\b',  # "US users", "EU law"
            r'\b(?:comply|compliance)\s+with\s+(' + '|'.join(escaped_locations[:30]) + r')\b',  # "comply with GDPR"
        ])
        
        # Age-specific jurisdiction patterns  
        location_pattern_parts.extend([
            r'\b(' + '|'.join(escaped_locations[:30]) + r')\s+(?:minors?|teens?|children|kids)\b',  # "California minors"
            r'\b(?:minors?|teens?|children|kids)\s+(?:in|from)\s+(' + '|'.join(escaped_locations[:30]) + r')\b',  # "minors in Utah"
        ])
        
        self.location_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in location_pattern_parts]
        
        # AGE PATTERNS (Clear age-related compliance indicators)
        age_pattern_parts = [
            r'\b(?:age|ages?)\s+(\d+)(?:\+|\s*and\s*(?:up|over|above))\b',  # "age 18+", "ages 13 and up"
            r'\b(?:under|below)\s+(?:age\s+)?(\d+)\b',  # "under 18", "under age 16"
            r'\b(\d+)(?:\+|\-)\s*(?:years?\s*old|yo)\b',  # "18+ years old", "21+ yo"
            r'\b(?:minors?|children|kids|teens?|teenagers|youth|juveniles?)\b',  # Age-related terms
            r'\b(?:parental\s+consent|guardian\s+permission|age\s+verification|age\s+gate)\b',  # Age verification terms
        ]
        
        # Add glossary age terms
        escaped_age_terms = [re.escape(term) for term in age_variants]
        age_pattern_parts.append(r'\b(' + '|'.join(escaped_age_terms[:30]) + r')\b')
        
        self.age_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in age_pattern_parts]
        
        # TERMINOLOGY PATTERNS (Clear regulatory/compliance indicators)
        terminology_pattern_parts = [
            r'\b(?:gdpr|general\s+data\s+protection\s+regulation)\b',
            r'\b(?:coppa|children\'?s\s+online\s+privacy\s+protection\s+act)\b',
            r'\b(?:ccpa|california\s+consumer\s+privacy\s+act)\b',
            r'\b(?:dsa|digital\s+services\s+act)\b',
            r'\b(?:ncmec|national\s+center\s+for\s+missing\s+.+\s+exploited\s+children)\b',
            r'\b(?:csam|child\s+sexual\s+abuse\s+material)\b',
            r'\b(?:age\s+appropriate\s+design\s+code|aadc)\b',
            r'\b(?:social\s+media\s+regulation\s+act)\b',
            r'\b(?:online\s+protections?\s+for\s+minors?)\b',
        ]
        
        # Add glossary terminology
        escaped_terms = [re.escape(term) for term in terminology_variants]
        terminology_pattern_parts.append(r'\b(' + '|'.join(escaped_terms[:30]) + r')\b')
        
        self.terminology_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in terminology_pattern_parts]
        
        # CLEAR-CUT COMPLIANCE PATTERNS (High confidence indicators)
        self.clear_cut_patterns = [
            re.compile(r'\b(?:comply|compliance)\s+with\s+(?:' + '|'.join(escaped_locations[:20]) + r')\s+(?:law|regulation|act|code)\b', re.IGNORECASE),
            re.compile(r'\b(?:' + '|'.join(escaped_locations[:20]) + r')\s+(?:law|regulation|act|code)\s+(?:compliance|requirement)\b', re.IGNORECASE),
            re.compile(r'\b(?:geo-?(?:fence|fencing|blocking|restriction)|geographic\s+restriction|location-based\s+(?:restriction|blocking))\b', re.IGNORECASE),
            re.compile(r'\b(?:age\s+(?:verification|gate|restriction)|parental\s+consent|minor\s+protection)\s+.+\s+(?:' + '|'.join(escaped_locations[:15]) + r')\b', re.IGNORECASE),
            re.compile(r'\b(?:' + '|'.join(escaped_locations[:15]) + r')\s+.+\s+(?:age\s+(?:verification|gate|restriction)|parental\s+consent|minor\s+protection)\b', re.IGNORECASE),
        ]
        
        logger.info("Compiled regex patterns for high-confidence detection")
    
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        if not text:
            return ""
        
        # Basic text cleaning
        text = text.strip()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Expand common abbreviations that might be missed
        abbreviation_map = {
            r'\bw\/': 'with',
            r'\b&': 'and', 
            r'\bu\.s\.': 'united states',
            r'\be\.u\.': 'european union',
            r'\bu\.k\.': 'united kingdom',
        }
        
        for pattern, replacement in abbreviation_map.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Advanced tokenization using regex (since we're using HuggingFace for NER)"""
        import re
        
        # Simple but effective tokenization
        # Split on word boundaries, keep alphanumeric tokens
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out very short tokens and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        filtered_tokens = []
        for token in tokens:
            if len(token) > 2 and token not in stop_words:
                filtered_tokens.append(token)
        
        return filtered_tokens
    
    def extract_entities_ner(self, text: str) -> List[EntityMatch]:
        """Extract entities using HuggingFace NER"""
        entities = []
        
        if not self.ner_pipeline:
            return entities  # No NER available
        
        try:
            # Get NER predictions
            ner_results = self.ner_pipeline(text)
            
            for ner_entity in ner_results:
                entity_type = None
                confidence = ner_entity.get('score', 0.7)
                
                # Map HuggingFace entity types to our types
                hf_label = ner_entity.get('entity_group', ner_entity.get('label', '')).upper()
                
                if hf_label in ["LOC", "LOCATION", "GPE"]:  # Location entities
                    entity_type = "LOCATION"
                    confidence = confidence * 0.9  # Slightly reduce for safety
                elif hf_label in ["ORG", "ORGANIZATION"]:
                    entity_type = "TERMINOLOGY"  # Organizations might be regulatory bodies
                    confidence = confidence * 0.8
                elif hf_label in ["PER", "PERSON"]:
                    # Persons might be relevant in regulatory context
                    entity_type = "TERMINOLOGY"
                    confidence = confidence * 0.6
                elif hf_label in ["MISC", "MISCELLANEOUS"]:
                    # Miscellaneous might include laws, acts, etc.
                    entity_type = "TERMINOLOGY"
                    confidence = confidence * 0.7
                
                if entity_type and confidence > 0.5:  # Only keep high-confidence entities
                    entity_text = ner_entity.get('word', '').strip()
                    
                    # Clean up subword tokens (remove ## prefixes)
                    entity_text = entity_text.replace('##', '')
                    
                    if len(entity_text) > 1:  # Filter out single characters
                        # Try to standardize using glossary
                        standardized_form = entity_text
                        if entity_type == "LOCATION":
                            location, gloss_conf = self.glossary.standardize_location(entity_text)
                            if location:
                                standardized_form = location.colloquial_name
                                confidence = max(confidence, gloss_conf * 0.9)
                        
                        entities.append(EntityMatch(
                            text=entity_text,
                            entity_type=entity_type,
                            start_pos=ner_entity.get('start', 0),
                            end_pos=ner_entity.get('end', len(entity_text)),
                            confidence=confidence,
                            standardized_form=standardized_form,
                            source="ner",
                            additional_info={"huggingface_label": hf_label}
                        ))
        
        except Exception as e:
            logger.error(f"Error in HuggingFace NER extraction: {e}")
        
        return entities
    
    def extract_entities_regex(self, text: str) -> List[EntityMatch]:
        """Extract entities using compiled regex patterns"""
        entities = []
        
        # Location entities
        for pattern in self.location_patterns:
            for match in pattern.finditer(text):
                matched_text = match.group(1) if match.groups() else match.group(0)
                
                # Standardize using glossary
                location, confidence = self.glossary.standardize_location(matched_text)
                if location:
                    entities.append(EntityMatch(
                        text=matched_text,
                        entity_type="LOCATION",
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=confidence,
                        standardized_form=location.colloquial_name,
                        source="regex",
                        additional_info={"pattern_type": "location"}
                    ))
        
        # Age entities  
        for pattern in self.age_patterns:
            for match in pattern.finditer(text):
                matched_text = match.group(1) if match.groups() else match.group(0)
                
                # Standardize using glossary
                age, confidence = self.glossary.standardize_age(matched_text)
                if age:
                    entities.append(EntityMatch(
                        text=matched_text,
                        entity_type="AGE",
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=confidence,
                        standardized_form=f"{age.term} ({age.numerical_range[0]}-{age.numerical_range[1]})",
                        source="regex",
                        additional_info={"numerical_range": age.numerical_range}
                    ))
        
        # Terminology entities
        for pattern in self.terminology_patterns:
            for match in pattern.finditer(text):
                matched_text = match.group(1) if match.groups() else match.group(0)
                
                # Standardize using glossary
                term, confidence = self.glossary.standardize_terminology(matched_text)
                if term:
                    entities.append(EntityMatch(
                        text=matched_text,
                        entity_type="TERMINOLOGY", 
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=confidence,
                        standardized_form=term.standardized_form,
                        source="regex",
                        additional_info={"category": term.category}
                    ))
        
        return entities
    
    def detect_clear_cut_cases(self, text: str, entities: List[EntityMatch]) -> Tuple[Optional[bool], float]:
        """
        Detect clear-cut geotagging cases with 95%+ confidence.
        Returns (needs_geo_logic, confidence_score)
        """
        
        # Check for explicit compliance patterns
        for pattern in self.clear_cut_patterns:
            if pattern.search(text):
                return True, 0.95  # Clear regulatory compliance language
        
        # Analyze entity combinations for high-confidence classification
        location_entities = [e for e in entities if e.entity_type == "LOCATION" and e.confidence >= 0.8]
        age_entities = [e for e in entities if e.entity_type == "AGE" and e.confidence >= 0.8]
        terminology_entities = [e for e in entities if e.entity_type == "TERMINOLOGY" and e.confidence >= 0.8]
        
        # High confidence indicators
        has_specific_location = any(e.confidence >= 0.9 for e in location_entities)
        has_age_verification = any("age" in e.text.lower() or "minor" in e.text.lower() for e in age_entities)
        has_compliance_terms = any(e.confidence >= 0.9 for e in terminology_entities)
        
        # Clear-cut cases (95%+ confidence)
        if has_specific_location and has_age_verification and has_compliance_terms:
            return True, 0.97  # Location + Age + Compliance = Very likely needs geo-logic
        
        if has_specific_location and has_compliance_terms:
            return True, 0.95  # Location + Compliance = Likely needs geo-logic
        
        # Strong business indicators (should NOT flag)
        business_indicators = [
            "market testing", "a/b test", "user engagement", "revenue", "conversion",
            "retention", "growth", "experiment", "pilot", "beta", "rollout", "launch"
        ]
        
        if any(indicator in text.lower() for indicator in business_indicators):
            # Check if there are also compliance indicators
            if not (has_compliance_terms or has_age_verification):
                return False, 0.90  # Business decision, not compliance
        
        # Not clear-cut - needs further analysis
        return None, 0.0
    
    def calculate_overall_confidence(self, entities: List[EntityMatch], clear_cut_result: Tuple[Optional[bool], float]) -> float:
        """Calculate overall confidence score for the preprocessing results"""
        
        if clear_cut_result[0] is not None:
            return clear_cut_result[1]  # Use clear-cut confidence
        
        # Calculate based on entity quality and quantity
        if not entities:
            return 0.3  # Low confidence due to no entities
        
        # Weight entities by type and confidence
        location_weight = 0.4
        age_weight = 0.3
        terminology_weight = 0.3
        
        location_score = max([e.confidence for e in entities if e.entity_type == "LOCATION"], default=0.0)
        age_score = max([e.confidence for e in entities if e.entity_type == "AGE"], default=0.0)
        terminology_score = max([e.confidence for e in entities if e.entity_type == "TERMINOLOGY"], default=0.0)
        
        weighted_score = (
            location_score * location_weight +
            age_score * age_weight +
            terminology_score * terminology_weight
        )
        
        # Boost score if multiple entity types detected
        entity_types = set(e.entity_type for e in entities)
        if len(entity_types) >= 2:
            weighted_score *= 1.2
        if len(entity_types) >= 3:
            weighted_score *= 1.1
        
        return min(weighted_score, 0.95)  # Cap at 95% for non-clear-cut cases
    
    def process(self, title: str, description: str) -> PreprocessingResult:
        """
        Main processing pipeline for feature classification.
        
        Args:
            title: Feature title
            description: Feature description
            
        Returns:
            PreprocessingResult with entities, classification, and confidence
        """
        
        # Combine title and description
        full_text = f"{title}. {description}".strip()
        
        # Preprocess text
        cleaned_text = self.preprocess_text(full_text)
        
        # Tokenize
        tokens = self.tokenize(cleaned_text)
        
        # Extract entities using both NER and regex
        ner_entities = self.extract_entities_ner(cleaned_text)
        regex_entities = self.extract_entities_regex(cleaned_text)
        
        # Combine and deduplicate entities
        all_entities = ner_entities + regex_entities
        
        # Simple deduplication based on overlap
        deduplicated_entities = []
        for entity in all_entities:
            # Check if this entity significantly overlaps with existing ones
            overlap = False
            for existing in deduplicated_entities:
                # If entities overlap by more than 50% and are same type, keep the higher confidence one
                overlap_start = max(entity.start_pos, existing.start_pos)
                overlap_end = min(entity.end_pos, existing.end_pos)
                overlap_length = max(0, overlap_end - overlap_start)
                
                entity_length = entity.end_pos - entity.start_pos
                existing_length = existing.end_pos - existing.start_pos
                
                overlap_ratio = overlap_length / min(entity_length, existing_length)
                
                if overlap_ratio > 0.5 and entity.entity_type == existing.entity_type:
                    if entity.confidence > existing.confidence:
                        # Replace existing with current entity
                        deduplicated_entities.remove(existing)
                        deduplicated_entities.append(entity)
                    overlap = True
                    break
            
            if not overlap:
                deduplicated_entities.append(entity)
        
        # Sort by confidence
        deduplicated_entities.sort(key=lambda x: x.confidence, reverse=True)
        
        # Detect clear-cut cases
        clear_cut_result = self.detect_clear_cut_cases(cleaned_text, deduplicated_entities)
        
        # Calculate overall confidence
        overall_confidence = self.calculate_overall_confidence(deduplicated_entities, clear_cut_result)
        
        # Determine if further analysis is needed
        needs_further_analysis = (
            clear_cut_result[0] is None or  # Not clear-cut
            overall_confidence < self.HIGH_CONFIDENCE_THRESHOLD  # Low confidence
        )
        
        return PreprocessingResult(
            original_text=full_text,
            cleaned_text=cleaned_text,
            tokens=tokens,
            entities=deduplicated_entities,
            clear_cut_classification=clear_cut_result[0],
            confidence_score=overall_confidence,
            needs_further_analysis=needs_further_analysis
        )

# Global preprocessor instance
_preprocessor_instance = None

def get_preprocessor() -> GeoCompliancePreprocessor:
    """Get singleton preprocessor instance"""
    global _preprocessor_instance
    if _preprocessor_instance is None:
        _preprocessor_instance = GeoCompliancePreprocessor()
    return _preprocessor_instance

if __name__ == "__main__":
    # Test the preprocessing pipeline
    preprocessor = GeoCompliancePreprocessor()
    
    # Test with a sample feature
    title = "Age verification system for California teens"
    description = "Implement age verification to comply with California SB976 for users under 18"
    
    result = preprocessor.process(title, description)
    
    print(f"Original text: {result.original_text}")
    print(f"Clear-cut classification: {result.clear_cut_classification}")
    print(f"Confidence: {result.confidence_score:.3f}")
    print(f"Needs further analysis: {result.needs_further_analysis}")
    print(f"Entities found: {len(result.entities)}")
    
    for entity in result.entities:
        print(f"  - {entity.text} ({entity.entity_type}) - {entity.confidence:.3f} - {entity.standardized_form}")
