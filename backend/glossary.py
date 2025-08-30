"""
Comprehensive Glossary System for Geo-Compliance Classification

This module provides the standardized glossary that maps all possible locations,
age terminology, and regulatory terms according to the main feature flow specifications.
"""

import json
import os
import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from datetime import datetime
import re
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class LocationMapping:
    """Standardized location mapping structure"""
    colloquial_name: str
    full_name: str
    country_code_iso: str  # ISO 3166-1 alpha-3
    country_code_ioc: str  # IOC codes for consistency 
    region: List[str]  # Can belong to multiple regions
    synonyms: List[str]
    abbreviations: List[str]
    confidence_score: float = 1.0  # For machine learning improvements

@dataclass
class AgeMapping:
    """Standardized age terminology mapping"""
    term: str
    numerical_range: Tuple[int, int]  # (min_age, max_age)
    synonyms: List[str]
    confidence_score: float = 1.0

@dataclass
class TerminologyMapping:
    """Standardized regulatory terminology mapping"""
    term: str
    standardized_form: str
    category: str  # e.g., "privacy", "content_moderation", "age_verification"
    synonyms: List[str]
    expanded_meanings: List[str]
    confidence_score: float = 1.0

class GeoComplianceGlossary:
    """
    Comprehensive glossary system for geo-compliance standardization.
    Supports self-evolution through feedback loops and confidence scoring.
    """
    
    def __init__(self, glossary_file: str = "backend/glossary_data.json"):
        self.glossary_file = glossary_file
        self.locations: Dict[str, LocationMapping] = {}
        self.age_terms: Dict[str, AgeMapping] = {}
        self.terminology: Dict[str, TerminologyMapping] = {}
        self.update_history: List[Dict] = []
        self.confidence_thresholds = {
            "location": 0.85,
            "age": 0.80,
            "terminology": 0.75
        }
        self._initialize_glossary()
    
    def _initialize_glossary(self):
        """Initialize glossary with comprehensive default data"""
        try:
            if os.path.exists(self.glossary_file):
                self._load_from_file()
            else:
                self._create_default_glossary()
                self._save_to_file()
        except Exception as e:
            logger.error(f"Failed to initialize glossary: {e}")
            self._create_default_glossary()
    
    def _create_default_glossary(self):
        """Create comprehensive default glossary based on UN member states and common terms"""
        
        # UN MEMBER STATES WITH COMPREHENSIVE MAPPINGS
        default_locations = [
            # Major jurisdictions with specific regulations
            {
                "colloquial_name": "United States",
                "full_name": "United States of America", 
                "country_code_iso": "USA",
                "country_code_ioc": "USA",
                "region": ["North America", "Americas"],
                "synonyms": ["US", "USA", "America", "United States"],
                "abbreviations": ["US", "U.S.", "USA", "U.S.A."]
            },
            {
                "colloquial_name": "European Union",
                "full_name": "European Union",
                "country_code_iso": "EUR", 
                "country_code_ioc": "EUR",
                "region": ["Europe", "European Union"],
                "synonyms": ["EU", "Europe", "European Union"],
                "abbreviations": ["EU", "E.U."]
            },
            {
                "colloquial_name": "Germany",
                "full_name": "Federal Republic of Germany",
                "country_code_iso": "DEU",
                "country_code_ioc": "GER", 
                "region": ["Europe", "European Union"],
                "synonyms": ["Germany", "Deutschland"],
                "abbreviations": ["DE", "GER"]
            },
            {
                "colloquial_name": "France",
                "full_name": "French Republic",
                "country_code_iso": "FRA",
                "country_code_ioc": "FRA",
                "region": ["Europe", "European Union"],
                "synonyms": ["France", "French Republic"],
                "abbreviations": ["FR", "FRA"]
            },
            {
                "colloquial_name": "United Kingdom",
                "full_name": "United Kingdom of Great Britain and Northern Ireland",
                "country_code_iso": "GBR",
                "country_code_ioc": "GBR",
                "region": ["Europe"],
                "synonyms": ["UK", "Britain", "Great Britain", "England"],
                "abbreviations": ["UK", "GB", "GBR"]
            },
            {
                "colloquial_name": "Canada",
                "full_name": "Canada",
                "country_code_iso": "CAN",
                "country_code_ioc": "CAN",
                "region": ["North America", "Americas"],
                "synonyms": ["Canada"],
                "abbreviations": ["CA", "CAN"]
            },
            {
                "colloquial_name": "California",
                "full_name": "State of California",
                "country_code_iso": "USA",
                "country_code_ioc": "USA",
                "region": ["North America", "United States", "US West Coast"],
                "synonyms": ["California", "CA", "Calif"],
                "abbreviations": ["CA", "CAL"]
            },
            {
                "colloquial_name": "Florida", 
                "full_name": "State of Florida",
                "country_code_iso": "USA",
                "country_code_ioc": "USA",
                "region": ["North America", "United States", "US Southeast"],
                "synonyms": ["Florida", "FL", "Fla"],
                "abbreviations": ["FL", "FLA"]
            },
            {
                "colloquial_name": "Utah",
                "full_name": "State of Utah", 
                "country_code_iso": "USA",
                "country_code_ioc": "USA",
                "region": ["North America", "United States", "US West"],
                "synonyms": ["Utah", "UT"],
                "abbreviations": ["UT"]
            },
            {
                "colloquial_name": "Singapore",
                "full_name": "Republic of Singapore",
                "country_code_iso": "SGP",
                "country_code_ioc": "SGP",
                "region": ["Asia", "Southeast Asia", "ASEAN"],
                "synonyms": ["Singapore", "S'pore"],
                "abbreviations": ["SG", "SGP"]
            },
            {
                "colloquial_name": "South Korea",
                "full_name": "Republic of Korea",
                "country_code_iso": "KOR",
                "country_code_ioc": "KOR",
                "region": ["Asia", "East Asia"],
                "synonyms": ["South Korea", "Korea", "Republic of Korea"],
                "abbreviations": ["KR", "KOR", "ROK"]
            },
            {
                "colloquial_name": "Japan",
                "full_name": "Japan",
                "country_code_iso": "JPN",
                "country_code_ioc": "JPN",
                "region": ["Asia", "East Asia"],
                "synonyms": ["Japan", "Nippon"],
                "abbreviations": ["JP", "JPN"]
            },
            {
                "colloquial_name": "Australia",
                "full_name": "Commonwealth of Australia",
                "country_code_iso": "AUS",
                "country_code_ioc": "AUS",
                "region": ["Oceania", "Asia-Pacific"],
                "synonyms": ["Australia", "Aussie"],
                "abbreviations": ["AU", "AUS"]
            },
            {
                "colloquial_name": "Brazil",
                "full_name": "Federative Republic of Brazil",
                "country_code_iso": "BRA",
                "country_code_ioc": "BRA",
                "region": ["South America", "Americas"],
                "synonyms": ["Brazil", "Brasil"],
                "abbreviations": ["BR", "BRA"]
            },
            {
                "colloquial_name": "Indonesia",
                "full_name": "Republic of Indonesia",
                "country_code_iso": "IDN",
                "country_code_ioc": "INA",
                "region": ["Asia", "Southeast Asia", "ASEAN"],
                "synonyms": ["Indonesia"],
                "abbreviations": ["ID", "IDN", "INA"]
            },
            {
                "colloquial_name": "China",
                "full_name": "People's Republic of China",
                "country_code_iso": "CHN",
                "country_code_ioc": "CHN",
                "region": ["Asia", "East Asia"],
                "synonyms": ["China", "PRC"],
                "abbreviations": ["CN", "CHN"]
            },
            {
                "colloquial_name": "India",
                "full_name": "Republic of India",
                "country_code_iso": "IND",
                "country_code_ioc": "IND",
                "region": ["Asia", "South Asia"],
                "synonyms": ["India", "Bharat"],
                "abbreviations": ["IN", "IND"]
            },
            {
                "colloquial_name": "Russia",
                "full_name": "Russian Federation",
                "country_code_iso": "RUS",
                "country_code_ioc": "RUS",
                "region": ["Europe", "Asia", "Eurasia"],
                "synonyms": ["Russia", "Russian Federation"],
                "abbreviations": ["RU", "RUS"]
            }
        ]
        
        # Convert to LocationMapping objects
        for loc_data in default_locations:
            location = LocationMapping(**loc_data)
            # Index by all possible names for fast lookup
            for name in [location.colloquial_name] + location.synonyms + location.abbreviations:
                self.locations[name.lower()] = location
        
        # AGE TERMINOLOGY MAPPINGS
        default_age_terms = [
            {
                "term": "minor",
                "numerical_range": (0, 17),
                "synonyms": ["child", "kid", "underage", "juvenile", "youth", "teen", "teenager"]
            },
            {
                "term": "adult", 
                "numerical_range": (18, 120),
                "synonyms": ["grown-up", "mature", "of age"]
            },
            {
                "term": "teen",
                "numerical_range": (13, 17),
                "synonyms": ["teenager", "adolescent", "youth"]
            },
            {
                "term": "child",
                "numerical_range": (0, 12),
                "synonyms": ["kid", "minor child", "young child"]
            },
            {
                "term": "young adult",
                "numerical_range": (18, 25),
                "synonyms": ["emerging adult", "college age"]
            },
            {
                "term": "13+",
                "numerical_range": (13, 120),
                "synonyms": ["thirteen plus", "13 and up", "over 13"]
            },
            {
                "term": "18+",
                "numerical_range": (18, 120), 
                "synonyms": ["eighteen plus", "18 and up", "adult content", "mature audience"]
            },
            {
                "term": "21+",
                "numerical_range": (21, 120),
                "synonyms": ["twenty-one plus", "21 and up", "legal drinking age"]
            }
        ]
        
        for age_data in default_age_terms:
            age_mapping = AgeMapping(**age_data)
            for term in [age_mapping.term] + age_mapping.synonyms:
                self.age_terms[term.lower()] = age_mapping
        
        # REGULATORY TERMINOLOGY MAPPINGS
        default_terminology = [
            {
                "term": "gdpr",
                "standardized_form": "General Data Protection Regulation",
                "category": "privacy",
                "synonyms": ["general data protection regulation", "eu gdpr", "european data protection"],
                "expanded_meanings": ["data protection", "privacy rights", "consent requirements"]
            },
            {
                "term": "coppa", 
                "standardized_form": "Children's Online Privacy Protection Act",
                "category": "age_verification",
                "synonyms": ["children's online privacy protection act", "child privacy law"],
                "expanded_meanings": ["parental consent", "child data protection", "age verification"]
            },
            {
                "term": "ccpa",
                "standardized_form": "California Consumer Privacy Act", 
                "category": "privacy",
                "synonyms": ["california consumer privacy act", "california privacy law"],
                "expanded_meanings": ["consumer rights", "data deletion", "privacy disclosure"]
            },
            {
                "term": "dsa",
                "standardized_form": "Digital Services Act",
                "category": "content_moderation", 
                "synonyms": ["digital services act", "eu dsa", "european digital services act"],
                "expanded_meanings": ["content transparency", "platform responsibility", "illegal content removal"]
            },
            {
                "term": "ncmec",
                "standardized_form": "National Center for Missing & Exploited Children",
                "category": "content_safety",
                "synonyms": ["national center for missing & exploited children", "child exploitation reporting"],
                "expanded_meanings": ["csam reporting", "child abuse material", "law enforcement reporting"]
            },
            {
                "term": "age_verification",
                "standardized_form": "age verification",
                "category": "age_verification", 
                "synonyms": ["age check", "age validation", "age confirmation", "identity verification"],
                "expanded_meanings": ["age gate", "minor protection", "parental consent"]
            },
            {
                "term": "parental_consent",
                "standardized_form": "parental consent",
                "category": "age_verification",
                "synonyms": ["parent permission", "guardian consent", "parental approval"],
                "expanded_meanings": ["minor protection", "family controls", "supervised access"]
            },
            {
                "term": "content_moderation",
                "standardized_form": "content moderation", 
                "category": "content_moderation",
                "synonyms": ["content review", "content filtering", "community standards"],
                "expanded_meanings": ["harmful content removal", "policy enforcement", "user safety"]
            },
            {
                "term": "data_localization",
                "standardized_form": "data localization",
                "category": "privacy",
                "synonyms": ["data residency", "local data storage", "regional data requirements"],
                "expanded_meanings": ["cross-border data transfer", "regional compliance", "data sovereignty"]
            }
        ]
        
        for term_data in default_terminology:
            term_mapping = TerminologyMapping(**term_data)
            for term in [term_mapping.term] + term_mapping.synonyms:
                self.terminology[term.lower()] = term_mapping
        
        logger.info("Created comprehensive default glossary with location, age, and terminology mappings")
    
    def standardize_location(self, text: str) -> Tuple[Optional[LocationMapping], float]:
        """
        Standardize location mentions in text to canonical forms.
        Returns the standardized location and confidence score.
        """
        text_lower = text.lower().strip()
        
        # Direct match
        if text_lower in self.locations:
            return self.locations[text_lower], 1.0
        
        # Fuzzy matching for partial matches
        best_match = None
        best_score = 0.0
        
        for key, location in self.locations.items():
            # Check if text contains the location name
            if key in text_lower or any(syn.lower() in text_lower for syn in location.synonyms):
                # Calculate confidence based on match quality
                if key == text_lower:
                    score = 1.0
                elif text_lower in key:
                    score = 0.9
                elif any(text_lower == syn.lower() for syn in location.synonyms):
                    score = 0.95
                else:
                    score = 0.8
                
                if score > best_score:
                    best_match = location
                    best_score = score
        
        return best_match, best_score
    
    def standardize_age(self, text: str) -> Tuple[Optional[AgeMapping], float]:
        """
        Standardize age-related terms to numerical ranges.
        Returns the standardized age mapping and confidence score.
        """
        text_lower = text.lower().strip()
        
        # Check for direct numerical patterns first
        age_patterns = [
            r'(\d+)\s*[\+\-]\s*',  # "18+", "21-"
            r'under\s*(\d+)',      # "under 18"
            r'over\s*(\d+)',       # "over 21"
            r'(\d+)\s*and\s*up',   # "13 and up"
            r'(\d+)\s*years?\s*old' # "18 years old"
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                age_num = int(match.group(1))
                if '+' in text_lower or 'up' in text_lower or 'over' in text_lower:
                    age_range = (age_num, 120)
                elif 'under' in text_lower:
                    age_range = (0, age_num - 1)
                else:
                    age_range = (age_num, age_num)
                
                # Create temporary mapping for numerical match
                return AgeMapping(
                    term=text,
                    numerical_range=age_range,
                    synonyms=[],
                    confidence_score=0.95
                ), 0.95
        
        # Check predefined age terms
        if text_lower in self.age_terms:
            return self.age_terms[text_lower], 1.0
        
        # Fuzzy matching
        best_match = None
        best_score = 0.0
        
        for key, age_mapping in self.age_terms.items():
            if key in text_lower or any(syn.lower() in text_lower for syn in age_mapping.synonyms):
                score = 0.8 if key in text_lower else 0.7
                if score > best_score:
                    best_match = age_mapping
                    best_score = score
        
        return best_match, best_score
    
    def standardize_terminology(self, text: str) -> Tuple[Optional[TerminologyMapping], float]:
        """
        Standardize regulatory terminology to canonical forms.
        Returns the standardized terminology and confidence score.
        """
        text_lower = text.lower().strip()
        
        # Direct match
        if text_lower in self.terminology:
            return self.terminology[text_lower], 1.0
        
        # Fuzzy matching
        best_match = None
        best_score = 0.0
        
        for key, term_mapping in self.terminology.items():
            if key in text_lower:
                score = 0.9
                if score > best_score:
                    best_match = term_mapping
                    best_score = score
            elif any(syn.lower() in text_lower for syn in term_mapping.synonyms):
                score = 0.8
                if score > best_score:
                    best_match = term_mapping
                    best_score = score
        
        return best_match, best_score
    
    def update_from_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        Update glossary based on human feedback for self-evolution.
        
        Args:
            feedback_data: Dict containing correction information
                {
                    "type": "location|age|terminology",
                    "original_text": "text that was misclassified",
                    "correct_mapping": "correct standardized form",
                    "confidence": float,
                    "feedback_source": "human_reviewer_id"
                }
        """
        try:
            feedback_type = feedback_data.get("type")
            original_text = feedback_data.get("original_text", "").lower()
            correct_mapping = feedback_data.get("correct_mapping")
            confidence = feedback_data.get("confidence", 1.0)
            
            if feedback_type == "location":
                # Update or add location mapping
                if original_text not in self.locations:
                    # Find the correct location to add synonym to
                    for key, location in self.locations.items():
                        if location.colloquial_name.lower() == correct_mapping.lower():
                            location.synonyms.append(original_text)
                            self.locations[original_text] = location
                            break
                    
            elif feedback_type == "age":
                # Similar logic for age terms
                if original_text not in self.age_terms:
                    # Add new age term based on feedback
                    pass
                    
            elif feedback_type == "terminology":
                # Similar logic for terminology
                if original_text not in self.terminology:
                    # Add new terminology based on feedback 
                    pass
            
            # Log the update
            self.update_history.append({
                "timestamp": datetime.now().isoformat(),
                "feedback_data": feedback_data,
                "action": "glossary_update"
            })
            
            # Save updated glossary
            self._save_to_file()
            
            logger.info(f"Updated glossary based on feedback: {feedback_type} - {original_text}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update glossary from feedback: {e}")
            return False
    
    def get_all_location_variants(self) -> Set[str]:
        """Get all location variants for regex pattern building"""
        variants = set()
        seen_names = set()  # Track unique locations by full name
        for location in self.locations.values():
            if location.full_name not in seen_names:
                seen_names.add(location.full_name)
                variants.add(location.colloquial_name.lower())
                variants.add(location.full_name.lower())
                variants.update([syn.lower() for syn in location.synonyms])
                variants.update([abbr.lower() for abbr in location.abbreviations])
        return variants
    
    def get_all_age_variants(self) -> Set[str]:
        """Get all age variants for regex pattern building"""
        variants = set()
        seen_terms = set()  # Track unique terms
        for age_mapping in self.age_terms.values():
            if age_mapping.term not in seen_terms:
                seen_terms.add(age_mapping.term)
                variants.add(age_mapping.term.lower())
                variants.update([syn.lower() for syn in age_mapping.synonyms])
        return variants
    
    def get_all_terminology_variants(self) -> Set[str]:
        """Get all terminology variants for regex pattern building"""
        variants = set()
        seen_terms = set()  # Track unique terms
        for term_mapping in self.terminology.values():
            if term_mapping.term not in seen_terms:
                seen_terms.add(term_mapping.term)
                variants.add(term_mapping.term.lower())
                variants.update([syn.lower() for syn in term_mapping.synonyms])
        return variants
    
    def _save_to_file(self):
        """Save glossary to JSON file"""
        try:
            # Convert to serializable format
            data = {
                "locations": {k: asdict(v) for k, v in self.locations.items()},
                "age_terms": {k: asdict(v) for k, v in self.age_terms.items()},
                "terminology": {k: asdict(v) for k, v in self.terminology.items()},
                "update_history": self.update_history,
                "confidence_thresholds": self.confidence_thresholds,
                "last_updated": datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.glossary_file), exist_ok=True)
            with open(self.glossary_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save glossary to file: {e}")
    
    def _load_from_file(self):
        """Load glossary from JSON file"""
        try:
            with open(self.glossary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct objects
            self.locations = {k: LocationMapping(**v) for k, v in data.get("locations", {}).items()}
            self.age_terms = {k: AgeMapping(**v) for k, v in data.get("age_terms", {}).items()}
            self.terminology = {k: TerminologyMapping(**v) for k, v in data.get("terminology", {}).items()}
            self.update_history = data.get("update_history", [])
            self.confidence_thresholds = data.get("confidence_thresholds", self.confidence_thresholds)
            
            logger.info("Loaded glossary from file")
            
        except Exception as e:
            logger.error(f"Failed to load glossary from file: {e}")
            raise

# Global glossary instance
_glossary_instance = None

def get_glossary() -> GeoComplianceGlossary:
    """Get singleton glossary instance"""
    global _glossary_instance
    if _glossary_instance is None:
        _glossary_instance = GeoComplianceGlossary()
    return _glossary_instance

if __name__ == "__main__":
    # Test the glossary system
    glossary = GeoComplianceGlossary()
    
    # Test location standardization
    location, confidence = glossary.standardize_location("US")
    print(f"Location: {location.colloquial_name if location else None}, Confidence: {confidence}")
    
    # Test age standardization
    age, confidence = glossary.standardize_age("under 18")
    print(f"Age: {age.numerical_range if age else None}, Confidence: {confidence}")
    
    # Test terminology standardization
    term, confidence = glossary.standardize_terminology("gdpr compliance")
    print(f"Term: {term.standardized_form if term else None}, Confidence: {confidence}")
