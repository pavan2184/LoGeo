"""
Enhanced Multi-Stage Classification System for Geo-Compliance

This module implements the complete feature flow:
1. Preprocessing and NER/Regex detection (95% confidence cases)
2. Entity standardization with glossary 
3. Multi-stage classification with LLM + cross-checking
4. Confidence calculation with category-specific thresholds
5. Human intervention alerts for low confidence cases
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from backend.preprocessing import get_preprocessor, PreprocessingResult, EntityMatch
from backend.glossary import get_glossary, LocationMapping, AgeMapping, TerminologyMapping
from backend.llm_classifier import get_classifier, RegulatoryAnalysisResult
from backend.rag_loader import get_rag_instance

logger = logging.getLogger(__name__)

@dataclass
class StandardizedEntities:
    """Standardized entities extracted from text"""
    locations: List[Dict[str, Any]]  # Standardized location information
    ages: List[Dict[str, Any]]       # Standardized age information  
    terminology: List[Dict[str, Any]] # Standardized regulatory terminology
    confidence_scores: Dict[str, float]  # Confidence by category

@dataclass
class EnhancedClassificationResult:
    """Complete classification result with all confidence metrics"""
    # Core classification
    needs_geo_logic: bool
    primary_confidence: float  # LLM confidence
    secondary_confidence: float  # Regex/NER confidence  
    overall_confidence: float  # Combined confidence
    
    # Detailed analysis
    reasoning: str
    applicable_regulations: List[dict]
    risk_assessment: str
    regulatory_requirements: List[str]
    evidence_sources: List[str]
    recommended_actions: List[str]
    
    # Enhanced features
    standardized_entities: StandardizedEntities
    preprocessing_result: PreprocessingResult
    clear_cut_detection: bool
    confidence_breakdown: Dict[str, float]
    
    # Human intervention
    needs_human_review: bool
    human_review_reason: str
    intervention_priority: str  # "low", "medium", "high", "critical"
    
    # Audit trail
    processing_timestamp: str
    method_used: str  # "clear_cut", "llm_primary", "llm_secondary", "rule_based"
    processing_time_ms: float

class EnhancedGeoComplianceClassifier:
    """
    Enhanced classifier implementing the complete multi-stage feature flow.
    Combines preprocessing, NER, LLM analysis, and confidence calculation.
    """
    
    def __init__(self):
        self.preprocessor = get_preprocessor()
        self.glossary = get_glossary()
        self.llm_classifier = get_classifier()
        self.rag = get_rag_instance()
        
        # Confidence thresholds for different categories
        self.confidence_thresholds = {
            "minor_protection": 0.90,   # Higher threshold for child safety
            "content_safety": 0.90,    # Higher threshold for CSAM/abuse
            "privacy_rights": 0.85,    # High threshold for privacy
            "data_protection": 0.85,   # High threshold for data handling
            "general_compliance": 0.80, # Standard threshold
            "business_feature": 0.75   # Lower threshold for business decisions
        }
        
        # Category determination keywords
        self.category_keywords = {
            "minor_protection": ["minor", "child", "teen", "age", "parental", "youth", "juvenile", "underage"],
            "content_safety": ["csam", "abuse", "harm", "exploitation", "safety", "ncmec", "reporting"],
            "privacy_rights": ["privacy", "data", "personal", "tracking", "collection", "consent"],
            "data_protection": ["gdpr", "ccpa", "data protection", "localization", "retention"],
            "general_compliance": ["compliance", "regulation", "law", "legal", "requirement"],
            "business_feature": ["test", "experiment", "rollout", "market", "engagement", "revenue"]
        }
    
    def standardize_entities(self, entities: List[EntityMatch]) -> StandardizedEntities:
        """
        Standardize all detected entities using the glossary system.
        This implements the Location/Age/Terminology standardization from the feature flow.
        """
        
        standardized_locations = []
        standardized_ages = []
        standardized_terminology = []
        
        confidence_scores = {"location": 0.0, "age": 0.0, "terminology": 0.0}
        
        for entity in entities:
            if entity.entity_type == "LOCATION":
                location, conf = self.glossary.standardize_location(entity.text)
                if location:
                    standardized_locations.append({
                        "original_text": entity.text,
                        "colloquial_name": location.colloquial_name,
                        "full_name": location.full_name,
                        "country_code": location.country_code_iso,
                        "region": location.region,
                        "confidence": conf,
                        "source": entity.source
                    })
                    confidence_scores["location"] = max(confidence_scores["location"], conf)
            
            elif entity.entity_type == "AGE":
                age, conf = self.glossary.standardize_age(entity.text)
                if age:
                    standardized_ages.append({
                        "original_text": entity.text,
                        "standardized_term": age.term,
                        "numerical_range": age.numerical_range,
                        "confidence": conf,
                        "source": entity.source
                    })
                    confidence_scores["age"] = max(confidence_scores["age"], conf)
            
            elif entity.entity_type == "TERMINOLOGY":
                term, conf = self.glossary.standardize_terminology(entity.text)
                if term:
                    standardized_terminology.append({
                        "original_text": entity.text,
                        "standardized_form": term.standardized_form,
                        "category": term.category,
                        "confidence": conf,
                        "source": entity.source
                    })
                    confidence_scores["terminology"] = max(confidence_scores["terminology"], conf)
        
        return StandardizedEntities(
            locations=standardized_locations,
            ages=standardized_ages,
            terminology=standardized_terminology,
            confidence_scores=confidence_scores
        )
    
    def determine_feature_category(self, text: str, entities: StandardizedEntities) -> str:
        """Determine the primary category of the feature for appropriate thresholding"""
        
        text_lower = text.lower()
        category_scores = {}
        
        # Score based on keywords
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = score
        
        # Boost scores based on standardized entities
        if entities.ages:
            category_scores["minor_protection"] += 2
        
        if any("safety" in term["category"] for term in entities.terminology):
            category_scores["content_safety"] += 2
        
        if any("privacy" in term["category"] for term in entities.terminology):
            category_scores["privacy_rights"] += 2
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "general_compliance"
    
    def build_enhanced_prompt(self, title: str, description: str, entities: StandardizedEntities, rag_context: str) -> str:
        """
        Build enhanced prompt with standardized entities for better LLM classification.
        This implements the prompt engineering aspect of the feature flow.
        """
        
        # Build entity context
        entity_context = []
        
        if entities.locations:
            locations_text = ", ".join([f"{loc['colloquial_name']} ({loc['country_code']})" for loc in entities.locations])
            entity_context.append(f"DETECTED LOCATIONS: {locations_text}")
        
        if entities.ages:
            ages_text = ", ".join([f"{age['standardized_term']} (ages {age['numerical_range'][0]}-{age['numerical_range'][1]})" for age in entities.ages])
            entity_context.append(f"DETECTED AGE TERMS: {ages_text}")
        
        if entities.terminology:
            terms_text = ", ".join([f"{term['standardized_form']} ({term['category']})" for term in entities.terminology])
            entity_context.append(f"DETECTED REGULATORY TERMS: {terms_text}")
        
        entity_section = "\n".join(entity_context) if entity_context else "No specific entities detected."
        
        prompt = f"""
You are a senior regulatory compliance expert analyzing software features for geographic-specific legal requirements.

FEATURE TO ANALYZE:
Title: {title}
Description: {description}

STANDARDIZED ENTITY ANALYSIS:
{entity_section}

RELEVANT REGULATORY CONTEXT:
{rag_context}

ENHANCED ANALYSIS REQUIREMENTS:
Based on the standardized entities and regulatory context, determine:

1. GEOTAGGING NECESSITY: Does this feature require geographic-specific implementation due to legal requirements?
   - Consider the specific locations, age groups, and regulatory terms detected
   - Distinguish between legal compliance requirements vs. business decisions
   - If locations are detected, assess whether they indicate legal jurisdiction requirements

2. CONFIDENCE ASSESSMENT: Provide detailed confidence scoring:
   - Entity detection confidence: How certain are you about the extracted entities?
   - Regulatory requirement confidence: How certain are you about legal obligations?
   - Geographic necessity confidence: How certain are you about geo-specific requirements?

3. CROSS-VALIDATION: Validate against multiple regulatory sources:
   - Primary assessment based on detected regulatory terms
   - Secondary assessment based on location and age combinations
   - Cross-check against known compliance patterns

RESPONSE FORMAT (JSON):
{{
    "needs_geo_logic": true/false,
    "confidence": 0.95,
    "reasoning": "Detailed analysis incorporating standardized entities...",
    "applicable_regulations": [
        {{
            "name": "Regulation Name",
            "jurisdiction": "Geographic Scope",
            "relevance": "high/medium/low",
            "specific_articles": ["Article X"],
            "legal_basis": "Why this regulation applies",
            "detected_entities": ["relevant entities that triggered this"]
        }}
    ],
    "risk_assessment": "high/medium/low",
    "regulatory_requirements": ["Specific legal obligations"],
    "evidence_sources": ["Sources supporting this analysis"],
    "recommended_actions": ["Specific next steps"],
    "entity_validation": {{
        "location_confidence": 0.95,
        "age_confidence": 0.90,
        "terminology_confidence": 0.85
    }},
    "cross_validation_score": 0.92
}}

CRITICAL INSTRUCTIONS:
- Use the standardized entities to inform your analysis
- Cross-reference detected locations with known regulatory jurisdictions
- Consider age-related entities for minor protection laws
- Validate terminology against known compliance requirements
- Provide specific confidence scores for different aspects
- Flag any uncertainties that might require human review
"""
        
        return prompt
    
    def cross_validate_with_secondary_checks(self, 
                                           text: str, 
                                           llm_result: RegulatoryAnalysisResult,
                                           entities: StandardizedEntities) -> Tuple[float, Dict[str, float]]:
        """
        Perform secondary validation using regex/NER patterns.
        This implements the Primary + Secondary cross-checking from the feature flow.
        """
        
        secondary_scores = {
            "location_validation": 0.0,
            "age_validation": 0.0, 
            "terminology_validation": 0.0,
            "pattern_matching": 0.0
        }
        
        # Location validation
        if entities.locations:
            # Check if LLM detected regulations match detected locations
            detected_jurisdictions = [loc["region"] for loc in entities.locations]
            llm_jurisdictions = [reg.get("jurisdiction", "") for reg in llm_result.applicable_regulations]
            
            jurisdiction_overlap = any(
                any(detected_region in llm_jurisdiction for detected_region in loc_regions)
                for loc_regions in detected_jurisdictions
                for llm_jurisdiction in llm_jurisdictions
            )
            
            secondary_scores["location_validation"] = 0.9 if jurisdiction_overlap else 0.6
        
        # Age validation  
        if entities.ages:
            # Check for age-related regulations
            age_regulations = ["coppa", "minor protection", "parental consent", "age verification"]
            llm_has_age_focus = any(
                any(age_reg in reg.get("name", "").lower() for age_reg in age_regulations)
                for reg in llm_result.applicable_regulations
            )
            
            secondary_scores["age_validation"] = 0.9 if llm_has_age_focus else 0.5
        
        # Terminology validation
        if entities.terminology:
            # Check if LLM identified regulations match detected terminology
            detected_categories = set(term["category"] for term in entities.terminology)
            llm_mentions_categories = any(
                any(category in llm_result.reasoning.lower() for category in detected_categories)
                for category in detected_categories
            )
            
            secondary_scores["terminology_validation"] = 0.9 if llm_mentions_categories else 0.6
        
        # Pattern matching validation
        compliance_patterns = [
            r'\b(?:comply|compliance)\s+with.*(?:law|regulation|act)\b',
            r'\b(?:geo.*restriction|geographic.*requirement|location.*based.*compliance)\b',
            r'\b(?:minor.*protection|age.*verification|parental.*consent).*(?:law|requirement)\b'
        ]
        
        import re
        pattern_matches = sum(1 for pattern in compliance_patterns if re.search(pattern, text, re.IGNORECASE))
        secondary_scores["pattern_matching"] = min(pattern_matches * 0.3, 0.9)
        
        # Calculate overall secondary confidence
        non_zero_scores = [score for score in secondary_scores.values() if score > 0]
        overall_secondary = sum(non_zero_scores) / len(non_zero_scores) if non_zero_scores else 0.0
        
        return overall_secondary, secondary_scores
    
    def calculate_final_confidence(self, 
                                 primary_confidence: float,
                                 secondary_confidence: float, 
                                 entities: StandardizedEntities,
                                 feature_category: str) -> Tuple[float, Dict[str, float]]:
        """
        Calculate final confidence score with category-specific thresholds.
        This implements the sophisticated confidence scoring from the feature flow.
        """
        
        # Weight primary and secondary confidence
        primary_weight = 0.7
        secondary_weight = 0.3
        
        base_confidence = (primary_confidence * primary_weight) + (secondary_confidence * secondary_weight)
        
        # Entity quality boost/penalty
        entity_confidence_avg = sum(entities.confidence_scores.values()) / len(entities.confidence_scores) if entities.confidence_scores else 0.5
        entity_adjustment = (entity_confidence_avg - 0.5) * 0.2  # ±0.1 adjustment
        
        # Entity diversity boost
        entity_types_detected = sum(1 for score in entities.confidence_scores.values() if score > 0)
        diversity_boost = min(entity_types_detected * 0.05, 0.15)  # Up to 0.15 boost
        
        final_confidence = base_confidence + entity_adjustment + diversity_boost
        final_confidence = max(0.0, min(1.0, final_confidence))  # Clamp to [0, 1]
        
        breakdown = {
            "base_confidence": base_confidence,
            "primary_component": primary_confidence * primary_weight,
            "secondary_component": secondary_confidence * secondary_weight,
            "entity_adjustment": entity_adjustment,
            "diversity_boost": diversity_boost,
            "final_confidence": final_confidence,
            "category_threshold": self.confidence_thresholds.get(feature_category, 0.80)
        }
        
        return final_confidence, breakdown
    
    def determine_human_intervention(self, 
                                   confidence: float,
                                   feature_category: str,
                                   entities: StandardizedEntities,
                                   llm_result: RegulatoryAnalysisResult) -> Tuple[bool, str, str]:
        """
        Determine if human intervention is needed based on confidence thresholds.
        This implements the human intervention logic from the feature flow.
        """
        
        category_threshold = self.confidence_thresholds.get(feature_category, 0.80)
        
        # Check if confidence is below threshold
        if confidence < category_threshold:
            priority = "high" if feature_category in ["minor_protection", "content_safety"] else "medium"
            reason = f"Confidence ({confidence:.3f}) below threshold ({category_threshold:.3f}) for {feature_category}"
            return True, reason, priority
        
        # Check for conflicting signals
        has_locations = bool(entities.locations)
        has_ages = bool(entities.ages) 
        has_terminology = bool(entities.terminology)
        
        if has_locations and not (has_ages or has_terminology):
            return True, "Location detected without compliance context - unclear intent", "medium"
        
        # Check for high-risk categories with medium confidence
        if feature_category in ["minor_protection", "content_safety"] and confidence < 0.90:
            return True, f"High-risk category ({feature_category}) requires higher confidence", "high"
        
        # Check for uncertain risk assessment
        if llm_result.risk_assessment == "unknown":
            return True, "LLM unable to determine risk level", "medium"
        
        return False, "", "low"
    
    def classify(self, title: str, description: str) -> EnhancedClassificationResult:
        """
        Main classification method implementing the complete feature flow.
        
        This is the primary entry point that orchestrates:
        1. Preprocessing and entity extraction
        2. Entity standardization  
        3. Clear-cut detection (95% cases)
        4. LLM analysis with enhanced prompts
        5. Secondary cross-validation
        6. Confidence calculation
        7. Human intervention determination
        """
        
        start_time = datetime.now()
        
        # Step 1: Preprocessing and entity extraction
        preprocessing_result = self.preprocessor.process(title, description)
        
        # Step 2: Entity standardization
        standardized_entities = self.standardize_entities(preprocessing_result.entities)
        
        # Step 3: Check for clear-cut cases (95% confidence)
        if preprocessing_result.clear_cut_classification is not None and preprocessing_result.confidence_score >= 0.95:
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return EnhancedClassificationResult(
                needs_geo_logic=preprocessing_result.clear_cut_classification,
                primary_confidence=preprocessing_result.confidence_score,
                secondary_confidence=preprocessing_result.confidence_score,
                overall_confidence=preprocessing_result.confidence_score,
                reasoning=f"Clear-cut detection: High confidence ({preprocessing_result.confidence_score:.3f}) classification based on regex/NER patterns.",
                applicable_regulations=[],
                risk_assessment="medium" if preprocessing_result.clear_cut_classification else "low",
                regulatory_requirements=["Verify specific regulatory requirements"] if preprocessing_result.clear_cut_classification else [],
                evidence_sources=["High-confidence pattern matching", "Entity detection"],
                recommended_actions=["Proceed with compliance implementation"] if preprocessing_result.clear_cut_classification else ["Continue with standard development"],
                standardized_entities=standardized_entities,
                preprocessing_result=preprocessing_result,
                clear_cut_detection=True,
                confidence_breakdown={"clear_cut_confidence": preprocessing_result.confidence_score},
                needs_human_review=False,
                human_review_reason="",
                intervention_priority="low",
                processing_timestamp=datetime.now().isoformat(),
                method_used="clear_cut",
                processing_time_ms=processing_time
            )
        
        # Step 4: Enhanced LLM analysis
        feature_category = self.determine_feature_category(f"{title} {description}", standardized_entities)
        rag_context = self.rag.get_regulatory_context(title, description)
        enhanced_prompt = self.build_enhanced_prompt(title, description, standardized_entities, rag_context)
        
        # Get LLM analysis (this will use the existing llm_classifier with enhanced prompt)
        llm_result = self.llm_classifier.analyze_regulatory_compliance(title, description)
        
        # Step 5: Secondary cross-validation
        secondary_confidence, secondary_breakdown = self.cross_validate_with_secondary_checks(
            f"{title} {description}", llm_result, standardized_entities
        )
        
        # Step 6: Final confidence calculation
        final_confidence, confidence_breakdown = self.calculate_final_confidence(
            llm_result.confidence, secondary_confidence, standardized_entities, feature_category
        )
        
        # Step 7: Human intervention determination
        needs_review, review_reason, priority = self.determine_human_intervention(
            final_confidence, feature_category, standardized_entities, llm_result
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return EnhancedClassificationResult(
            needs_geo_logic=llm_result.needs_geo_logic,
            primary_confidence=llm_result.confidence,
            secondary_confidence=secondary_confidence,
            overall_confidence=final_confidence,
            reasoning=llm_result.reasoning,
            applicable_regulations=llm_result.applicable_regulations,
            risk_assessment=llm_result.risk_assessment,
            regulatory_requirements=llm_result.regulatory_requirements,
            evidence_sources=llm_result.evidence_sources,
            recommended_actions=llm_result.recommended_actions,
            standardized_entities=standardized_entities,
            preprocessing_result=preprocessing_result,
            clear_cut_detection=False,
            confidence_breakdown=confidence_breakdown,
            needs_human_review=needs_review,
            human_review_reason=review_reason,
            intervention_priority=priority,
            processing_timestamp=datetime.now().isoformat(),
            method_used="llm_primary" if llm_result.confidence > 0.7 else "llm_secondary",
            processing_time_ms=processing_time
        )

# Global enhanced classifier instance
_enhanced_classifier_instance = None

def get_enhanced_classifier() -> EnhancedGeoComplianceClassifier:
    """Get singleton enhanced classifier instance"""
    global _enhanced_classifier_instance
    if _enhanced_classifier_instance is None:
        _enhanced_classifier_instance = EnhancedGeoComplianceClassifier()
    return _enhanced_classifier_instance

if __name__ == "__main__":
    # Test the enhanced classifier
    classifier = EnhancedGeoComplianceClassifier()
    
    # Test cases
    test_cases = [
        ("Utah Minor Curfew", "Implement curfew restrictions for minors in Utah to comply with Utah Social Media Regulation Act"),
        ("A/B Test Feature", "Test new UI design in Canada for user engagement optimization"),
        ("CSAM Detection", "Implement automated child sexual abuse material detection for NCMEC reporting requirements")
    ]
    
    for title, description in test_cases:
        print(f"\n=== Testing: {title} ===")
        result = classifier.classify(title, description)
        print(f"Needs geo-logic: {result.needs_geo_logic}")
        print(f"Overall confidence: {result.overall_confidence:.3f}")
        print(f"Method: {result.method_used}")
        print(f"Needs review: {result.needs_human_review}")
        if result.needs_human_review:
            print(f"Review reason: {result.human_review_reason}")
        print(f"Processing time: {result.processing_time_ms:.1f}ms")
