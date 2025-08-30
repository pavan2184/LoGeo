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

@dataclass
class ThresholdRule:
    """Classification threshold rule with escalation logic"""
    confidence_threshold: float
    escalation_rule: str  # "human_review", "auto_ok", "ignore"
    description: str
    categories: List[str]  # Categories that map to this threshold
    priority: str  # "high", "medium", "low"
    below_threshold_action: str  # "human", "auto_ok", "ignore"

@dataclass
class EscalationDecision:
    """Result of threshold evaluation with escalation decision"""
    threshold_rule_name: str
    confidence: float
    threshold: float
    meets_threshold: bool
    escalation_action: str  # "human_review", "auto_approve", "ignore"
    priority: str
    reasoning: str

@dataclass
class GlossaryVersion:
    """Version information for glossary tracking"""
    version: str  # e.g., "1.2.3"
    timestamp: str
    description: str
    changes: List[str]  # List of changes made in this version
    author: str = "system"

@dataclass
class ChangelogEntry:
    """Individual changelog entry for glossary updates"""
    version: str
    timestamp: str
    change_type: str  # "addition", "modification", "deletion", "migration"
    entity_type: str  # "location", "age", "terminology", "threshold_rule"
    entity_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: str = ""
    author: str = "system"

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
        self.update_history: List[Dict] = []  # Legacy format - kept for compatibility
        self.confidence_thresholds = {
            "location": 0.85,
            "age": 0.80,
            "terminology": 0.75
        }
        self.classification_thresholds: Dict[str, ThresholdRule] = {}
        
        # Enhanced versioning system
        self.current_version: str = "1.0.0"
        self.version_history: List[GlossaryVersion] = []
        self.changelog: List[ChangelogEntry] = []
        
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
            },
            # Additional comprehensive examples for better coverage
            {
                "colloquial_name": "Mexico",
                "full_name": "United Mexican States",
                "country_code_iso": "MEX",
                "country_code_ioc": "MEX",
                "region": ["North America", "Americas", "Latin America"],
                "synonyms": ["Mexico", "Mexican States"],
                "abbreviations": ["MX", "MEX"]
            },
            {
                "colloquial_name": "South Africa",
                "full_name": "Republic of South Africa", 
                "country_code_iso": "ZAF",
                "country_code_ioc": "RSA",
                "region": ["Africa", "Southern Africa"],
                "synonyms": ["South Africa", "RSA"],
                "abbreviations": ["ZA", "ZAF", "RSA"]
            },
            {
                "colloquial_name": "New Zealand",
                "full_name": "New Zealand",
                "country_code_iso": "NZL",
                "country_code_ioc": "NZL",
                "region": ["Oceania", "Asia-Pacific"],
                "synonyms": ["New Zealand", "NZ", "Aotearoa"],
                "abbreviations": ["NZ", "NZL"]
            },
            {
                "colloquial_name": "Netherlands",
                "full_name": "Kingdom of the Netherlands",
                "country_code_iso": "NLD",
                "country_code_ioc": "NED",
                "region": ["Europe", "European Union", "Western Europe"],
                "synonyms": ["Netherlands", "Holland", "Dutch"],
                "abbreviations": ["NL", "NLD", "NED"]
            },
            {
                "colloquial_name": "Switzerland",
                "full_name": "Swiss Confederation",
                "country_code_iso": "CHE",
                "country_code_ioc": "SUI",
                "region": ["Europe", "Western Europe"],
                "synonyms": ["Switzerland", "Swiss Confederation"],
                "abbreviations": ["CH", "CHE", "SUI"]
            },
            {
                "colloquial_name": "Norway",
                "full_name": "Kingdom of Norway",
                "country_code_iso": "NOR",
                "country_code_ioc": "NOR", 
                "region": ["Europe", "Northern Europe", "Scandinavia", "Nordic Countries"],
                "synonyms": ["Norway", "Kingdom of Norway"],
                "abbreviations": ["NO", "NOR"]
            },
            {
                "colloquial_name": "Turkey",
                "full_name": "Republic of Turkey",
                "country_code_iso": "TUR",
                "country_code_ioc": "TUR",
                "region": ["Europe", "Asia", "Middle East"],
                "synonyms": ["Turkey", "Türkiye"],
                "abbreviations": ["TR", "TUR"]
            },
            {
                "colloquial_name": "Israel",
                "full_name": "State of Israel",
                "country_code_iso": "ISR",
                "country_code_ioc": "ISR",
                "region": ["Asia", "Middle East"],
                "synonyms": ["Israel", "State of Israel"],
                "abbreviations": ["IL", "ISR"]
            },
            {
                "colloquial_name": "Thailand",
                "full_name": "Kingdom of Thailand",
                "country_code_iso": "THA",
                "country_code_ioc": "THA",
                "region": ["Asia", "Southeast Asia", "ASEAN"],
                "synonyms": ["Thailand", "Siam"],
                "abbreviations": ["TH", "THA"]
            },
            {
                "colloquial_name": "Malaysia",
                "full_name": "Malaysia",
                "country_code_iso": "MYS",
                "country_code_ioc": "MAS",
                "region": ["Asia", "Southeast Asia", "ASEAN"],
                "synonyms": ["Malaysia"],
                "abbreviations": ["MY", "MYS", "MAS"]
            },
            {
                "colloquial_name": "Philippines",
                "full_name": "Republic of the Philippines",
                "country_code_iso": "PHL",
                "country_code_ioc": "PHI",
                "region": ["Asia", "Southeast Asia", "ASEAN"],
                "synonyms": ["Philippines", "Filipino"],
                "abbreviations": ["PH", "PHL", "PHI"]
            },
            {
                "colloquial_name": "Vietnam",
                "full_name": "Socialist Republic of Vietnam",
                "country_code_iso": "VNM",
                "country_code_ioc": "VIE",
                "region": ["Asia", "Southeast Asia", "ASEAN"],
                "synonyms": ["Vietnam", "Viet Nam"],
                "abbreviations": ["VN", "VNM", "VIE"]
            },
            # Regional and Economic Zone Examples
            {
                "colloquial_name": "Southeast Asia",
                "full_name": "Southeast Asian Region",
                "country_code_iso": "SEA",
                "country_code_ioc": "SEA",
                "region": ["Asia", "Southeast Asia"],
                "synonyms": ["SEA", "ASEAN region", "South East Asia"],
                "abbreviations": ["SEA", "ASEAN"]
            },
            {
                "colloquial_name": "Middle East",
                "full_name": "Middle Eastern Region", 
                "country_code_iso": "MEA",
                "country_code_ioc": "MEA",
                "region": ["Asia", "Africa", "Middle East"],
                "synonyms": ["Middle East", "MENA", "Near East"],
                "abbreviations": ["ME", "MEA", "MENA"]
            },
            {
                "colloquial_name": "Latin America",
                "full_name": "Latin American Region",
                "country_code_iso": "LAT",
                "country_code_ioc": "LAT", 
                "region": ["Americas", "South America", "Central America"],
                "synonyms": ["Latin America", "LATAM", "South America"],
                "abbreviations": ["LAT", "LATAM"]
            },
            {
                "colloquial_name": "Nordic Countries",
                "full_name": "Nordic Region",
                "country_code_iso": "NOR",
                "country_code_ioc": "NOR",
                "region": ["Europe", "Northern Europe", "Scandinavia"],
                "synonyms": ["Nordic", "Scandinavia", "Northern Europe"],
                "abbreviations": ["NOR", "SCAN"]
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
            },
            # Additional comprehensive age term examples
            {
                "term": "infant",
                "numerical_range": (0, 2),
                "synonyms": ["baby", "newborn", "toddler under 2"]
            },
            {
                "term": "preschooler",
                "numerical_range": (3, 5),
                "synonyms": ["preschool age", "pre-k", "kindergarten age"]
            },
            {
                "term": "school age",
                "numerical_range": (6, 12),
                "synonyms": ["elementary age", "primary school", "grade school"]
            },
            {
                "term": "preteen",
                "numerical_range": (10, 12),
                "synonyms": ["tween", "pre-adolescent", "middle schooler"]
            },
            {
                "term": "high schooler",
                "numerical_range": (14, 18),
                "synonyms": ["high school student", "secondary school", "grades 9-12"]
            },
            {
                "term": "college student",
                "numerical_range": (18, 22),
                "synonyms": ["university student", "undergraduate", "college age"]
            },
            {
                "term": "working age",
                "numerical_range": (18, 65),
                "synonyms": ["adult workforce", "employable age", "career age"]
            },
            {
                "term": "senior citizen",
                "numerical_range": (65, 120),
                "synonyms": ["elderly", "retirement age", "golden years", "65+"]
            },
            {
                "term": "16+",
                "numerical_range": (16, 120),
                "synonyms": ["sixteen plus", "driving age", "16 and older"]
            },
            {
                "term": "25+",
                "numerical_range": (25, 120),
                "synonyms": ["twenty-five plus", "mature adult", "25 and up"]
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
            },
            # Additional comprehensive regulatory terminology examples
            {
                "term": "pipl",
                "standardized_form": "Personal Information Protection Law",
                "category": "privacy",
                "synonyms": ["personal information protection law", "china pipl", "chinese data protection"],
                "expanded_meanings": ["personal data protection", "consent requirements", "data processing rights"]
            },
            {
                "term": "lgpd",
                "standardized_form": "Lei Geral de Proteção de Dados",
                "category": "privacy",
                "synonyms": ["lei geral de proteção de dados", "brazil data protection", "brazilian privacy law"],
                "expanded_meanings": ["personal data protection", "data subject rights", "data processing consent"]
            },
            {
                "term": "utah_social_media_act",
                "standardized_form": "Utah Social Media Regulation Act",
                "category": "age_verification",
                "synonyms": ["utah social media regulation act", "utah minor protection"],
                "expanded_meanings": ["minor protection", "social media curfew", "parental controls"]
            },
            {
                "term": "florida_minor_protections",
                "standardized_form": "Florida Social Media Age Verification Requirements",
                "category": "age_verification",
                "synonyms": ["florida age verification", "fl minor protection", "florida social media law"],
                "expanded_meanings": ["age verification", "minor protection", "parental consent"]
            },
            {
                "term": "uk_age_appropriate_design",
                "standardized_form": "UK Age Appropriate Design Code",
                "category": "age_verification",
                "synonyms": ["uk age appropriate design code", "uk children's code", "ico children's code"],
                "expanded_meanings": ["children's privacy", "age-appropriate design", "data minimization"]
            },
            {
                "term": "kosa",
                "standardized_form": "Kids Online Safety Act",
                "category": "content_safety",
                "synonyms": ["kids online safety act", "us kids safety", "child online protection"],
                "expanded_meanings": ["online safety", "social media protection", "mental health protection"]
            },
            {
                "term": "csam",
                "standardized_form": "Child Sexual Abuse Material",
                "category": "content_safety",
                "synonyms": ["child sexual abuse material", "child exploitation material", "illegal content"],
                "expanded_meanings": ["law enforcement reporting", "content moderation", "child protection"]
            },
            {
                "term": "right_to_be_forgotten",
                "standardized_form": "Right to Erasure",
                "category": "privacy",
                "synonyms": ["right to erasure", "data deletion rights", "forgetting rights"],
                "expanded_meanings": ["data deletion", "privacy rights", "personal data removal"]
            },
            {
                "term": "nis2",
                "standardized_form": "Network and Information Security Directive 2",
                "category": "security_compliance",
                "synonyms": ["nis2 directive", "network information security", "eu cybersecurity"],
                "expanded_meanings": ["cybersecurity requirements", "incident reporting", "risk management"]
            },
            {
                "term": "ai_act",
                "standardized_form": "EU Artificial Intelligence Act",
                "category": "regulatory_compliance",
                "synonyms": ["eu ai act", "artificial intelligence act", "ai regulation"],
                "expanded_meanings": ["ai governance", "algorithmic transparency", "ai risk assessment"]
            },
            {
                "term": "online_safety_bill",
                "standardized_form": "UK Online Safety Act",
                "category": "content_moderation",
                "synonyms": ["uk online safety act", "online safety bill", "uk content regulation"],
                "expanded_meanings": ["duty of care", "content moderation", "user safety"]
            },
            {
                "term": "gdpr_article_6",
                "standardized_form": "GDPR Article 6 - Lawfulness of Processing",
                "category": "privacy",
                "synonyms": ["gdpr lawful basis", "legal basis processing", "article 6 gdpr"],
                "expanded_meanings": ["lawful basis", "consent", "legitimate interest"]
            },
            {
                "term": "gdpr_article_17",
                "standardized_form": "GDPR Article 17 - Right to Erasure",
                "category": "privacy",
                "synonyms": ["right to erasure", "right to be forgotten", "data deletion"],
                "expanded_meanings": ["data deletion", "erasure rights", "personal data removal"]
            },
            {
                "term": "dma",
                "standardized_form": "Digital Markets Act",
                "category": "regulatory_compliance",
                "synonyms": ["digital markets act", "eu dma", "gatekeeper regulation"],
                "expanded_meanings": ["platform regulation", "gatekeeper obligations", "market fairness"]
            },
            {
                "term": "cpra",
                "standardized_form": "California Privacy Rights Act",
                "category": "privacy",
                "synonyms": ["california privacy rights act", "ccpa amendment", "enhanced california privacy"],
                "expanded_meanings": ["sensitive personal information", "data sharing limits", "privacy rights"]
            },
            {
                "term": "vcdpa",
                "standardized_form": "Virginia Consumer Data Protection Act",
                "category": "privacy",
                "synonyms": ["virginia consumer data protection act", "virginia privacy law"],
                "expanded_meanings": ["consumer rights", "data processing", "privacy disclosure"]
            },
            {
                "term": "transparency_reporting",
                "standardized_form": "Content Moderation Transparency Reporting",
                "category": "content_moderation",
                "synonyms": ["transparency reports", "content moderation reports", "compliance reporting"],
                "expanded_meanings": ["content statistics", "moderation metrics", "regulatory reporting"]
            },
            {
                "term": "age_assurance",
                "standardized_form": "Age Assurance and Verification",
                "category": "age_verification",
                "synonyms": ["age assurance", "age estimation", "identity verification"],
                "expanded_meanings": ["age verification", "identity checking", "minor protection"]
            }
        ]
        
        for term_data in default_terminology:
            term_mapping = TerminologyMapping(**term_data)
            for term in [term_mapping.term] + term_mapping.synonyms:
                self.terminology[term.lower()] = term_mapping
        
        # CLASSIFICATION THRESHOLD RULES
        default_threshold_rules = {
            "legal_compliance": ThresholdRule(
                confidence_threshold=0.90,
                escalation_rule="human_review",
                description="Legal / Compliance requirements",
                categories=["minor_protection", "content_safety", "privacy_rights", "data_protection", "regulatory_compliance"],
                priority="high",
                below_threshold_action="human"
            ),
            "safety_health_protection": ThresholdRule(
                confidence_threshold=0.85,
                escalation_rule="human_review",
                description="Safety / Health Protection",
                categories=["user_safety", "health_protection", "harm_prevention", "security_compliance"],
                priority="medium",
                below_threshold_action="human"
            ),
            "business_non_binding": ThresholdRule(
                confidence_threshold=0.70,
                escalation_rule="auto_ok",
                description="Business (non-binding)",
                categories=["business_feature", "market_testing", "user_experience", "performance_optimization"],
                priority="low",
                below_threshold_action="auto_ok"
            ),
            "internal_analytics": ThresholdRule(
                confidence_threshold=0.60,
                escalation_rule="ignore",
                description="Internal Analytics only",
                categories=["analytics", "metrics", "internal_monitoring", "development_tools"],
                priority="low",
                below_threshold_action="ignore"
            )
        }
        
        self.classification_thresholds = default_threshold_rules
        
        # Initialize versioning for new glossary
        self._initialize_versioning()
        
        logger.info("Created comprehensive default glossary with location, age, terminology mappings, and threshold rules")
    
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
        Update glossary based on human feedback for self-evolution with versioning.
        
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
            feedback_source = feedback_data.get("feedback_source", "human_reviewer")
            
            changes_made = []
            
            if feedback_type == "location":
                # Update or add location mapping
                if original_text not in self.locations:
                    # Find the correct location to add synonym to
                    for key, location in self.locations.items():
                        if location.colloquial_name.lower() == correct_mapping.lower():
                            old_synonyms = location.synonyms.copy()
                            location.synonyms.append(original_text)
                            self.locations[original_text] = location
                            
                            # Add changelog entry
                            self.add_changelog_entry(
                                change_type="modification",
                                entity_type="location",
                                entity_name=location.colloquial_name,
                                old_value=str(old_synonyms),
                                new_value=str(location.synonyms),
                                reason=f"Added synonym from human feedback: {original_text}",
                                author=feedback_source
                            )
                            changes_made.append(f"Added synonym '{original_text}' to location '{location.colloquial_name}'")
                            break
                    
            elif feedback_type == "age":
                # Similar logic for age terms with versioning
                if original_text not in self.age_terms:
                    changes_made.append(f"Age term feedback processed: {original_text}")
                    self.add_changelog_entry(
                        change_type="addition",
                        entity_type="age",
                        entity_name=original_text,
                        new_value=correct_mapping,
                        reason="Added from human feedback",
                        author=feedback_source
                    )
                    
            elif feedback_type == "terminology":
                # Similar logic for terminology with versioning
                if original_text not in self.terminology:
                    changes_made.append(f"Terminology feedback processed: {original_text}")
                    self.add_changelog_entry(
                        change_type="addition",
                        entity_type="terminology",
                        entity_name=original_text,
                        new_value=correct_mapping,
                        reason="Added from human feedback", 
                        author=feedback_source
                    )
            
            # Increment version if changes were made
            if changes_made:
                self.increment_version(
                    version_type="patch",
                    description=f"Human feedback integration: {feedback_type}",
                    changes=changes_made
                )
            
            # Log the update (legacy format)
            self.update_history.append({
                "timestamp": datetime.now().isoformat(),
                "feedback_data": feedback_data,
                "action": "glossary_update",
                "version": self.current_version,
                "changes": changes_made
            })
            
            # Save updated glossary
            self._save_to_file()
            
            logger.info(f"Updated glossary based on feedback: {feedback_type} - {original_text} (v{self.current_version})")
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
    
    def evaluate_threshold(self, category: str, confidence: float) -> EscalationDecision:
        """Evaluate confidence against threshold rules and determine escalation action"""
        
        # Find the threshold rule that applies to this category
        applicable_rule = None
        rule_name = None
        
        for rule_name_candidate, rule in self.classification_thresholds.items():
            if category in rule.categories:
                applicable_rule = rule
                rule_name = rule_name_candidate
                break
        
        # Default to general compliance if no specific rule found
        if not applicable_rule:
            # Try to find a general rule or create a default
            for rule_name_candidate, rule in self.classification_thresholds.items():
                if "general" in rule_name_candidate.lower() or "compliance" in rule_name_candidate.lower():
                    applicable_rule = rule
                    rule_name = rule_name_candidate
                    break
            
            # If still no rule, use legal_compliance as safest default
            if not applicable_rule:
                rule_name = "legal_compliance"
                applicable_rule = self.classification_thresholds.get(rule_name)
        
        if not applicable_rule:
            # Emergency fallback - should not happen if properly configured
            return EscalationDecision(
                threshold_rule_name="fallback",
                confidence=confidence,
                threshold=0.80,
                meets_threshold=confidence >= 0.80,
                escalation_action="human_review",
                priority="high",
                reasoning="No threshold rule found - using conservative fallback"
            )
        
        meets_threshold = confidence >= applicable_rule.confidence_threshold
        
        # Determine escalation action
        if meets_threshold:
            escalation_action = "auto_approve"
            reasoning = f"Confidence ({confidence:.3f}) meets threshold ({applicable_rule.confidence_threshold:.3f})"
        else:
            escalation_action = applicable_rule.below_threshold_action
            if escalation_action == "human":
                escalation_action = "human_review"
            reasoning = f"Confidence ({confidence:.3f}) below threshold ({applicable_rule.confidence_threshold:.3f}) - {applicable_rule.below_threshold_action}"
        
        return EscalationDecision(
            threshold_rule_name=rule_name,
            confidence=confidence,
            threshold=applicable_rule.confidence_threshold,
            meets_threshold=meets_threshold,
            escalation_action=escalation_action,
            priority=applicable_rule.priority,
            reasoning=reasoning
        )
    
    def get_threshold_rule(self, rule_name: str) -> Optional[ThresholdRule]:
        """Get a specific threshold rule by name"""
        return self.classification_thresholds.get(rule_name)
    
    def get_all_threshold_rules(self) -> Dict[str, ThresholdRule]:
        """Get all threshold rules"""
        return self.classification_thresholds.copy()
    
    def update_threshold_rule(self, rule_name: str, threshold_rule: ThresholdRule) -> bool:
        """Update or add a threshold rule"""
        try:
            self.classification_thresholds[rule_name] = threshold_rule
            
            # Log the update
            self.update_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "threshold_rule_update",
                "rule_name": rule_name,
                "rule_data": asdict(threshold_rule)
            })
            
            self._save_to_file()
            logger.info(f"Updated threshold rule: {rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update threshold rule {rule_name}: {e}")
            return False
    
    def map_category_to_threshold_rule(self, category: str) -> Optional[str]:
        """Map a feature category to its applicable threshold rule"""
        for rule_name, rule in self.classification_thresholds.items():
            if category in rule.categories:
                return rule_name
        return None
    
    def increment_version(self, version_type: str = "patch", description: str = "", changes: List[str] = None) -> str:
        """
        Increment version number using semantic versioning.
        
        Args:
            version_type: "major", "minor", or "patch"
            description: Description of changes in this version
            changes: List of specific changes made
        
        Returns:
            New version string
        """
        changes = changes or []
        major, minor, patch = map(int, self.current_version.split('.'))
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        
        # Create version record
        version_record = GlossaryVersion(
            version=new_version,
            timestamp=datetime.now().isoformat(),
            description=description or f"Automated {version_type} update",
            changes=changes
        )
        
        # Update versioning
        self.version_history.append(version_record)
        self.current_version = new_version
        
        logger.info(f"Glossary version updated: {self.current_version}")
        return new_version
    
    def add_changelog_entry(self, 
                          change_type: str,
                          entity_type: str, 
                          entity_name: str,
                          old_value: Optional[str] = None,
                          new_value: Optional[str] = None,
                          reason: str = "",
                          author: str = "system") -> None:
        """Add entry to detailed changelog"""
        
        entry = ChangelogEntry(
            version=self.current_version,
            timestamp=datetime.now().isoformat(),
            change_type=change_type,
            entity_type=entity_type,
            entity_name=entity_name,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            author=author
        )
        
        self.changelog.append(entry)
        
    def get_version_history(self, limit: Optional[int] = None) -> List[GlossaryVersion]:
        """Get version history, optionally limited to recent versions"""
        history = sorted(self.version_history, key=lambda v: v.timestamp, reverse=True)
        return history[:limit] if limit else history
    
    def get_changelog(self, 
                     version: Optional[str] = None,
                     entity_type: Optional[str] = None,
                     limit: Optional[int] = None) -> List[ChangelogEntry]:
        """
        Get changelog entries with optional filtering.
        
        Args:
            version: Filter by specific version
            entity_type: Filter by entity type (location, age, terminology, threshold_rule)
            limit: Limit number of entries returned
        """
        filtered_entries = self.changelog
        
        if version:
            filtered_entries = [e for e in filtered_entries if e.version == version]
            
        if entity_type:
            filtered_entries = [e for e in filtered_entries if e.entity_type == entity_type]
        
        # Sort by timestamp (newest first)
        filtered_entries = sorted(filtered_entries, key=lambda e: e.timestamp, reverse=True)
        
        return filtered_entries[:limit] if limit else filtered_entries
    
    def export_version_report(self) -> Dict[str, Any]:
        """Export comprehensive version and changelog report"""
        return {
            "current_version": self.current_version,
            "version_history": [asdict(v) for v in self.get_version_history(10)],
            "recent_changes": [asdict(e) for e in self.get_changelog(limit=50)],
            "statistics": {
                "total_versions": len(self.version_history),
                "total_changelog_entries": len(self.changelog),
                "locations_count": len(set(l.full_name for l in self.locations.values())),
                "age_terms_count": len(set(a.term for a in self.age_terms.values())),
                "terminology_count": len(set(t.term for t in self.terminology.values())),
                "threshold_rules_count": len(self.classification_thresholds)
            },
            "change_summary_by_type": self._get_change_summary_by_type()
        }
    
    def _get_change_summary_by_type(self) -> Dict[str, int]:
        """Get summary of changes by type"""
        summary = {}
        for entry in self.changelog:
            key = f"{entry.entity_type}_{entry.change_type}"
            summary[key] = summary.get(key, 0) + 1
        return summary
    
    def _save_to_file(self):
        """Save glossary to JSON file with versioning information"""
        try:
            # Convert to serializable format
            data = {
                "locations": {k: asdict(v) for k, v in self.locations.items()},
                "age_terms": {k: asdict(v) for k, v in self.age_terms.items()},
                "terminology": {k: asdict(v) for k, v in self.terminology.items()},
                "classification_thresholds": {k: asdict(v) for k, v in self.classification_thresholds.items()},
                "update_history": self.update_history,  # Legacy format
                "confidence_thresholds": self.confidence_thresholds,
                
                # Enhanced versioning data
                "current_version": self.current_version,
                "version_history": [asdict(v) for v in self.version_history],
                "changelog": [asdict(e) for e in self.changelog],
                
                "last_updated": datetime.now().isoformat(),
                "schema_version": "2.0.0"  # Format versioning
            }
            
            os.makedirs(os.path.dirname(self.glossary_file), exist_ok=True)
            with open(self.glossary_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save glossary to file: {e}")
    
    def _load_from_file(self):
        """Load glossary from JSON file with versioning support"""
        try:
            with open(self.glossary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct objects
            self.locations = {k: LocationMapping(**v) for k, v in data.get("locations", {}).items()}
            self.age_terms = {k: AgeMapping(**v) for k, v in data.get("age_terms", {}).items()}
            self.terminology = {k: TerminologyMapping(**v) for k, v in data.get("terminology", {}).items()}
            self.classification_thresholds = {k: ThresholdRule(**v) for k, v in data.get("classification_thresholds", {}).items()}
            self.update_history = data.get("update_history", [])  # Legacy format
            self.confidence_thresholds = data.get("confidence_thresholds", self.confidence_thresholds)
            
            # Load versioning data (if available)
            self.current_version = data.get("current_version", "1.0.0")
            
            # Load version history
            version_history_data = data.get("version_history", [])
            self.version_history = [GlossaryVersion(**v) for v in version_history_data]
            
            # Load changelog
            changelog_data = data.get("changelog", [])
            self.changelog = [ChangelogEntry(**e) for e in changelog_data]
            
            # Check if this is a legacy file (no versioning)
            schema_version = data.get("schema_version")
            if not schema_version:
                # This is a legacy file - initialize versioning
                self._migrate_to_versioned_format()
            
            logger.info(f"Loaded glossary from file (version {self.current_version})")
            
            # Ensure threshold rules are initialized
            self._init_default_thresholds_if_missing()
            
        except Exception as e:
            logger.error(f"Failed to load glossary from file: {e}")
            raise
    
    def _migrate_to_versioned_format(self):
        """Migrate legacy glossary to versioned format"""
        logger.info("Migrating legacy glossary to versioned format")
        
        # Create initial version
        initial_version = GlossaryVersion(
            version="1.0.0",
            timestamp=datetime.now().isoformat(),
            description="Initial migration to versioned format",
            changes=["Migrated legacy glossary data to versioned format"],
            author="system"
        )
        
        self.version_history = [initial_version]
        self.current_version = "1.0.0"
        
        # Create migration changelog entries
        migration_entries = [
            ChangelogEntry(
                version="1.0.0",
                timestamp=datetime.now().isoformat(),
                change_type="migration",
                entity_type="location",
                entity_name="all_locations",
                new_value=f"Migrated {len(set(l.full_name for l in self.locations.values()))} unique locations",
                reason="Legacy format migration",
                author="system"
            ),
            ChangelogEntry(
                version="1.0.0",
                timestamp=datetime.now().isoformat(),
                change_type="migration",
                entity_type="age",
                entity_name="all_age_terms",
                new_value=f"Migrated {len(set(a.term for a in self.age_terms.values()))} unique age terms",
                reason="Legacy format migration", 
                author="system"
            ),
            ChangelogEntry(
                version="1.0.0",
                timestamp=datetime.now().isoformat(),
                change_type="migration",
                entity_type="terminology",
                entity_name="all_terminology",
                new_value=f"Migrated {len(set(t.term for t in self.terminology.values()))} unique terms",
                reason="Legacy format migration",
                author="system"
            )
        ]
        
        self.changelog = migration_entries
        
        # Save the migrated format
        self._save_to_file()
        
        logger.info("Successfully migrated glossary to versioned format")
    
    def _initialize_versioning(self):
        """Initialize versioning for new glossary"""
        # Create initial version
        initial_version = GlossaryVersion(
            version="1.0.0",
            timestamp=datetime.now().isoformat(),
            description="Initial glossary creation",
            changes=[
                "Created comprehensive location mappings with UN member states",
                "Initialized age terminology mappings",
                "Set up regulatory terminology database", 
                "Configured classification threshold rules"
            ],
            author="system"
        )
        
        self.version_history = [initial_version]
        self.current_version = "1.0.0"
        
        # Create initial changelog entries
        initial_entries = [
            ChangelogEntry(
                version="1.0.0",
                timestamp=datetime.now().isoformat(),
                change_type="addition",
                entity_type="location",
                entity_name="comprehensive_mappings",
                new_value="Added comprehensive location mappings for major jurisdictions",
                reason="Initial glossary setup",
                author="system"
            ),
            ChangelogEntry(
                version="1.0.0",
                timestamp=datetime.now().isoformat(),
                change_type="addition",
                entity_type="age",
                entity_name="age_terminology",
                new_value="Added standard age terminology mappings",
                reason="Initial glossary setup",
                author="system"
            ),
            ChangelogEntry(
                version="1.0.0",
                timestamp=datetime.now().isoformat(),
                change_type="addition",
                entity_type="terminology",
                entity_name="regulatory_terms",
                new_value="Added regulatory compliance terminology",
                reason="Initial glossary setup",
                author="system"
            ),
            ChangelogEntry(
                version="1.0.0",
                timestamp=datetime.now().isoformat(),
                change_type="addition",
                entity_type="threshold_rule",
                entity_name="classification_thresholds",
                new_value="Configured classification threshold rules",
                reason="Initial glossary setup",
                author="system"
            )
        ]
        
        self.changelog = initial_entries
    
    def _init_default_thresholds_if_missing(self):
        """Initialize default threshold rules if they don't exist"""
        if not self.classification_thresholds:
            default_threshold_rules = {
                "legal_compliance": ThresholdRule(
                    confidence_threshold=0.90,
                    escalation_rule="human_review",
                    description="Legal / Compliance requirements",
                    categories=["minor_protection", "content_safety", "privacy_rights", "data_protection", "regulatory_compliance"],
                    priority="high",
                    below_threshold_action="human"
                ),
                "safety_health_protection": ThresholdRule(
                    confidence_threshold=0.85,
                    escalation_rule="human_review",
                    description="Safety / Health Protection",
                    categories=["user_safety", "health_protection", "harm_prevention", "security_compliance"],
                    priority="medium",
                    below_threshold_action="human"
                ),
                "business_non_binding": ThresholdRule(
                    confidence_threshold=0.70,
                    escalation_rule="auto_ok",
                    description="Business (non-binding)",
                    categories=["business_feature", "market_testing", "user_experience", "performance_optimization"],
                    priority="low",
                    below_threshold_action="auto_ok"
                ),
                "internal_analytics": ThresholdRule(
                    confidence_threshold=0.60,
                    escalation_rule="ignore",
                    description="Internal Analytics only",
                    categories=["analytics", "metrics", "internal_monitoring", "development_tools"],
                    priority="low",
                    below_threshold_action="ignore"
                )
            }
            self.classification_thresholds = default_threshold_rules
            logger.info("Initialized default threshold rules")

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
    
    # Test threshold evaluation
    decision = glossary.evaluate_threshold("minor_protection", 0.95)
    print(f"Threshold Decision: {decision.escalation_action}, Rule: {decision.threshold_rule_name}")
    
    decision = glossary.evaluate_threshold("business_feature", 0.65)
    print(f"Threshold Decision: {decision.escalation_action}, Rule: {decision.threshold_rule_name}")
    
    decision = glossary.evaluate_threshold("analytics", 0.55)
    print(f"Threshold Decision: {decision.escalation_action}, Rule: {decision.threshold_rule_name}")
