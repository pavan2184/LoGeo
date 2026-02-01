"""
Ambiguity Handler for Geo-Compliance Classification

This module provides systematic handling for ambiguous cases where location/age 
entities are missing, vague, or unclear. Implements the decision framework:

- If entity is missing/vague but regionally relevant → assign "Unknown" + law cross-check
- If entity is completely unclear → flag for human intervention
- Provides disambiguation strategies and confidence assessment

Examples handled:
- "teen" → age ambiguity (13-17 range)
- "overseas" → location ambiguity (non-domestic)
- "Western Europe" → region ambiguity (multiple countries)
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)

class AmbiguityType(Enum):
    """Types of ambiguity in entity detection"""
    MISSING_LOCATION = "missing_location"
    VAGUE_LOCATION = "vague_location"
    MISSING_AGE = "missing_age"
    VAGUE_AGE = "vague_age"
    UNCLEAR_TERMINOLOGY = "unclear_terminology"
    REGIONAL_AMBIGUITY = "regional_ambiguity"
    TEMPORAL_AMBIGUITY = "temporal_ambiguity"

class AmbiguityResolution(Enum):
    """Resolution strategies for ambiguous cases"""
    ASSIGN_UNKNOWN = "assign_unknown"
    FLAG_HUMAN_REVIEW = "flag_human_review"
    INFER_FROM_CONTEXT = "infer_from_context"
    REQUEST_CLARIFICATION = "request_clarification"
    APPLY_DEFAULT_RULES = "apply_default_rules"

@dataclass
class AmbiguityAssessment:
    """Assessment of ambiguity in entity detection"""
    ambiguity_type: AmbiguityType
    confidence_impact: float  # How much this reduces overall confidence (0-1)
    entity_text: str
    context_clues: List[str]
    suggested_resolution: AmbiguityResolution
    resolution_confidence: float
    alternative_interpretations: List[str]
    requires_human_review: bool
    escalation_priority: str  # "low", "medium", "high"

@dataclass
class DisambiguationResult:
    """Result of ambiguity resolution process"""
    original_entity: str
    resolved_value: Optional[str]
    ambiguity_assessments: List[AmbiguityAssessment]
    overall_confidence_penalty: float
    recommended_action: str
    human_review_needed: bool
    context_used: List[str]

class AmbiguityHandler:
    """
    Systematic handler for ambiguous entity cases in geo-compliance classification.
    
    Provides:
    - Detection of ambiguous entities
    - Context-based disambiguation strategies
    - Confidence impact assessment
    - Human intervention triggers
    """
    
    def __init__(self):
        # Patterns for detecting vague location references
        self.vague_location_patterns = {
            "overseas": ["overseas", "abroad", "international", "foreign"],
            "domestic": ["domestic", "local", "national", "homeland"],
            "regional": ["western europe", "eastern europe", "southeast asia", "middle east", 
                        "latin america", "north africa", "sub-saharan africa", "nordic countries"],
            "continental": ["europe", "asia", "africa", "americas", "oceania"],
            "hemispheric": ["northern hemisphere", "southern hemisphere", "eastern hemisphere", "western hemisphere"],
            "economic_zones": ["eu", "nafta", "asean", "mercosur", "brics"]
        }
        
        # Patterns for detecting vague age references
        self.vague_age_patterns = {
            "teen": ["teen", "teenager", "adolescent"],
            "young_adult": ["young adult", "college age", "university age"],
            "adult": ["adult", "grown-up", "mature"],
            "elderly": ["elderly", "senior", "older adult"],
            "youth": ["youth", "young people", "kids"],
            "general": ["users", "people", "individuals", "persons"]
        }
        
        # Context clues for disambiguation
        self.context_clues = {
            "regulatory": ["gdpr", "ccpa", "coppa", "dsa", "law", "regulation", "compliance"],
            "business": ["market", "expansion", "launch", "rollout", "pilot"],
            "technical": ["server", "data center", "localization", "infrastructure"],
            "legal": ["jurisdiction", "court", "legal", "liability", "requirement"]
        }
        
        # Default resolutions for common ambiguous cases
        self.default_resolutions = {
            "teen": {"age_range": (13, 17), "requires_review": True, "confidence_penalty": 0.2},
            "overseas": {"location": "Unknown_International", "requires_review": True, "confidence_penalty": 0.3},
            "western europe": {"region": "Western_Europe", "requires_review": False, "confidence_penalty": 0.1},
            "adult": {"age_range": (18, 65), "requires_review": False, "confidence_penalty": 0.1}
        }
    
    def assess_ambiguity(self, 
                        entities: List[Dict[str, Any]], 
                        text: str, 
                        context: Dict[str, Any] = None) -> List[AmbiguityAssessment]:
        """
        Assess ambiguity in detected entities and provide resolution strategies.
        
        Args:
            entities: List of detected entities from preprocessing
            text: Original text being analyzed
            context: Additional context (feature category, regulatory signals, etc.)
        
        Returns:
            List of ambiguity assessments
        """
        context = context or {}
        assessments = []
        
        # Check for missing critical entities
        has_location = any(e.get("entity_type") == "LOCATION" for e in entities)
        has_age = any(e.get("entity_type") == "AGE" for e in entities)
        
        # Assess missing location
        if not has_location:
            assessment = self._assess_missing_location(text, context)
            if assessment:
                assessments.append(assessment)
        
        # Assess missing age
        if not has_age:
            assessment = self._assess_missing_age(text, context)
            if assessment:
                assessments.append(assessment)
        
        # Assess vague entities
        for entity in entities:
            entity_text = entity.get("text", "").lower()
            entity_type = entity.get("entity_type")
            
            if entity_type == "LOCATION":
                assessment = self._assess_location_ambiguity(entity_text, text, context)
                if assessment:
                    assessments.append(assessment)
            
            elif entity_type == "AGE":
                assessment = self._assess_age_ambiguity(entity_text, text, context)
                if assessment:
                    assessments.append(assessment)
        
        return assessments
    
    def _assess_missing_location(self, text: str, context: Dict[str, Any]) -> Optional[AmbiguityAssessment]:
        """Assess implications of missing location information"""
        
        # Check for regulatory context that might imply location relevance
        regulatory_signals = []
        for signal in self.context_clues["regulatory"]:
            if signal in text.lower():
                regulatory_signals.append(signal)
        
        if regulatory_signals:
            return AmbiguityAssessment(
                ambiguity_type=AmbiguityType.MISSING_LOCATION,
                confidence_impact=0.25,
                entity_text="<missing>",
                context_clues=regulatory_signals,
                suggested_resolution=AmbiguityResolution.ASSIGN_UNKNOWN,
                resolution_confidence=0.7,
                alternative_interpretations=["Feature may be location-agnostic", "Location implied by context"],
                requires_human_review=True,
                escalation_priority="medium"
            )
        
        return None
    
    def _assess_missing_age(self, text: str, context: Dict[str, Any]) -> Optional[AmbiguityAssessment]:
        """Assess implications of missing age information"""
        
        # Check for minor protection signals
        minor_signals = ["child", "minor", "parent", "guardian", "coppa", "age verification"]
        found_signals = [signal for signal in minor_signals if signal in text.lower()]
        
        if found_signals:
            return AmbiguityAssessment(
                ambiguity_type=AmbiguityType.MISSING_AGE,
                confidence_impact=0.3,
                entity_text="<missing>",
                context_clues=found_signals,
                suggested_resolution=AmbiguityResolution.FLAG_HUMAN_REVIEW,
                resolution_confidence=0.8,
                alternative_interpretations=["Age verification required", "Minor protection applicable"],
                requires_human_review=True,
                escalation_priority="high"
            )
        
        return None
    
    def _assess_location_ambiguity(self, entity_text: str, full_text: str, context: Dict[str, Any]) -> Optional[AmbiguityAssessment]:
        """Assess ambiguity in location entities"""
        
        # Check for vague location patterns
        for category, patterns in self.vague_location_patterns.items():
            if any(pattern in entity_text for pattern in patterns):
                
                confidence_impact = {
                    "overseas": 0.3,
                    "domestic": 0.2,
                    "regional": 0.15,
                    "continental": 0.25,
                    "hemispheric": 0.4,
                    "economic_zones": 0.1
                }.get(category, 0.2)
                
                requires_review = category in ["overseas", "hemispheric", "continental"]
                
                return AmbiguityAssessment(
                    ambiguity_type=AmbiguityType.VAGUE_LOCATION,
                    confidence_impact=confidence_impact,
                    entity_text=entity_text,
                    context_clues=self._extract_location_context(full_text),
                    suggested_resolution=AmbiguityResolution.ASSIGN_UNKNOWN if requires_review else AmbiguityResolution.INFER_FROM_CONTEXT,
                    resolution_confidence=0.6,
                    alternative_interpretations=self._get_location_alternatives(entity_text, category),
                    requires_human_review=requires_review,
                    escalation_priority="medium" if requires_review else "low"
                )
        
        return None
    
    def _assess_age_ambiguity(self, entity_text: str, full_text: str, context: Dict[str, Any]) -> Optional[AmbiguityAssessment]:
        """Assess ambiguity in age entities"""
        
        # Check for vague age patterns
        for category, patterns in self.vague_age_patterns.items():
            if any(pattern in entity_text for pattern in patterns):
                
                confidence_impact = {
                    "teen": 0.2,  # Relatively clear range
                    "young_adult": 0.25,
                    "adult": 0.3,  # Very broad
                    "elderly": 0.2,
                    "youth": 0.35,  # Very ambiguous
                    "general": 0.4   # No age specificity
                }.get(category, 0.25)
                
                requires_review = category in ["youth", "general", "adult"]
                
                return AmbiguityAssessment(
                    ambiguity_type=AmbiguityType.VAGUE_AGE,
                    confidence_impact=confidence_impact,
                    entity_text=entity_text,
                    context_clues=self._extract_age_context(full_text),
                    suggested_resolution=AmbiguityResolution.FLAG_HUMAN_REVIEW if requires_review else AmbiguityResolution.APPLY_DEFAULT_RULES,
                    resolution_confidence=0.7,
                    alternative_interpretations=self._get_age_alternatives(entity_text, category),
                    requires_human_review=requires_review,
                    escalation_priority="high" if category in ["youth", "general"] else "medium"
                )
        
        return None
    
    def _extract_location_context(self, text: str) -> List[str]:
        """Extract location-relevant context from text"""
        context_clues = []
        
        # Look for regulatory context
        for clue in self.context_clues["regulatory"]:
            if clue in text.lower():
                context_clues.append(f"regulatory_signal:{clue}")
        
        # Look for business context
        for clue in self.context_clues["business"]:
            if clue in text.lower():
                context_clues.append(f"business_signal:{clue}")
        
        return context_clues
    
    def _extract_age_context(self, text: str) -> List[str]:
        """Extract age-relevant context from text"""
        context_clues = []
        
        # Minor protection signals
        minor_signals = ["parental consent", "guardian", "supervision", "coppa", "child protection"]
        for signal in minor_signals:
            if signal in text.lower():
                context_clues.append(f"minor_protection:{signal}")
        
        # Age verification signals
        verification_signals = ["age verification", "id check", "identity verification", "age gate"]
        for signal in verification_signals:
            if signal in text.lower():
                context_clues.append(f"age_verification:{signal}")
        
        return context_clues
    
    def _get_location_alternatives(self, entity_text: str, category: str) -> List[str]:
        """Get alternative interpretations for location ambiguity"""
        alternatives = {
            "overseas": ["Non-domestic markets", "International users", "Global deployment"],
            "domestic": ["Home country only", "National scope", "Local implementation"],
            "regional": ["Multi-country region", "Economic zone", "Cultural region"],
            "continental": ["Continental scope", "Multiple regions", "Broad geographic area"],
            "hemispheric": ["Global scope", "Multi-continental", "Worldwide deployment"],
            "economic_zones": ["Trade bloc", "Economic partnership", "Regulatory union"]
        }
        return alternatives.get(category, ["Context-dependent interpretation"])
    
    def _get_age_alternatives(self, entity_text: str, category: str) -> List[str]:
        """Get alternative interpretations for age ambiguity"""
        alternatives = {
            "teen": ["13-17 years", "Adolescents", "High school age"],
            "young_adult": ["18-25 years", "College age", "Emerging adults"],
            "adult": ["18+ years", "General adult population", "All ages above minor"],
            "elderly": ["65+ years", "Senior citizens", "Retirement age"],
            "youth": ["Under 18", "Minors", "Children and teens"],
            "general": ["All ages", "Age-agnostic", "No age restriction"]
        }
        return alternatives.get(category, ["Age range unclear"])
    
    def resolve_ambiguities(self, 
                          assessments: List[AmbiguityAssessment],
                          use_defaults: bool = True) -> DisambiguationResult:
        """
        Resolve detected ambiguities using configured strategies.
        
        Args:
            assessments: List of ambiguity assessments
            use_defaults: Whether to apply default resolutions
        
        Returns:
            DisambiguationResult with resolved values and recommendations
        """
        
        overall_confidence_penalty = 0.0
        human_review_needed = False
        context_used = []
        resolved_entities = []
        
        for assessment in assessments:
            # Calculate cumulative confidence penalty
            overall_confidence_penalty += assessment.confidence_impact
            
            # Track human review requirements
            if assessment.requires_human_review:
                human_review_needed = True
            
            # Collect context used
            context_used.extend(assessment.context_clues)
            
            # Apply resolution strategy
            resolved_value = None
            if use_defaults and assessment.entity_text.lower() in self.default_resolutions:
                default = self.default_resolutions[assessment.entity_text.lower()]
                resolved_value = str(default)
            elif assessment.suggested_resolution == AmbiguityResolution.ASSIGN_UNKNOWN:
                resolved_value = f"Unknown_{assessment.ambiguity_type.value}"
            
            resolved_entities.append({
                "original": assessment.entity_text,
                "resolved": resolved_value,
                "confidence_penalty": assessment.confidence_impact
            })
        
        # Cap confidence penalty at 0.5 to prevent over-penalization
        overall_confidence_penalty = min(overall_confidence_penalty, 0.5)
        
        # Determine recommended action
        if overall_confidence_penalty > 0.3 or human_review_needed:
            recommended_action = "human_review"
        elif overall_confidence_penalty > 0.2:
            recommended_action = "elevated_confidence_threshold"
        else:
            recommended_action = "proceed_with_caution"
        
        return DisambiguationResult(
            original_entity=", ".join([a.entity_text for a in assessments]),
            resolved_value=str(resolved_entities) if resolved_entities else None,
            ambiguity_assessments=assessments,
            overall_confidence_penalty=overall_confidence_penalty,
            recommended_action=recommended_action,
            human_review_needed=human_review_needed,
            context_used=list(set(context_used))
        )
    
    def get_ambiguity_report(self, assessments: List[AmbiguityAssessment]) -> Dict[str, Any]:
        """Generate comprehensive ambiguity report"""
        
        if not assessments:
            return {"status": "no_ambiguity", "confidence_impact": 0.0}
        
        ambiguity_types = [a.ambiguity_type.value for a in assessments]
        total_confidence_impact = sum(a.confidence_impact for a in assessments)
        highest_priority = max([a.escalation_priority for a in assessments], 
                              key=lambda x: {"low": 1, "medium": 2, "high": 3}[x])
        
        return {
            "status": "ambiguity_detected",
            "total_assessments": len(assessments),
            "ambiguity_types": ambiguity_types,
            "total_confidence_impact": min(total_confidence_impact, 0.5),
            "highest_priority": highest_priority,
            "requires_human_review": any(a.requires_human_review for a in assessments),
            "summary": f"Detected {len(assessments)} ambiguous entities with {total_confidence_impact:.2f} confidence impact",
            "recommendations": [a.suggested_resolution.value for a in assessments]
        }

# Global ambiguity handler instance
_ambiguity_handler_instance = None

def get_ambiguity_handler() -> AmbiguityHandler:
    """Get singleton ambiguity handler instance"""
    global _ambiguity_handler_instance
    if _ambiguity_handler_instance is None:
        _ambiguity_handler_instance = AmbiguityHandler()
    return _ambiguity_handler_instance

if __name__ == "__main__":
    # Test the ambiguity handler
    handler = AmbiguityHandler()
    
    # Test cases for different ambiguity types
    test_cases = [
        {
            "entities": [{"entity_type": "AGE", "text": "teen"}],
            "text": "Age verification system for teen users on social platform",
            "context": {"feature_type": "age_verification"}
        },
        {
            "entities": [{"entity_type": "LOCATION", "text": "overseas"}],
            "text": "Expand content moderation overseas to comply with international regulations",
            "context": {"feature_type": "content_moderation"}
        },
        {
            "entities": [{"entity_type": "LOCATION", "text": "Western Europe"}],
            "text": "GDPR compliance for data processing in Western Europe",
            "context": {"feature_type": "data_protection"}
        },
        {
            "entities": [],
            "text": "User data analytics system for business insights",
            "context": {"feature_type": "analytics"}
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n=== Test Case {i+1} ===")
        assessments = handler.assess_ambiguity(case["entities"], case["text"], case["context"])
        
        if assessments:
            result = handler.resolve_ambiguities(assessments)
            report = handler.get_ambiguity_report(assessments)
            
            print(f"Ambiguities detected: {len(assessments)}")
            print(f"Confidence penalty: {result.overall_confidence_penalty:.3f}")
            print(f"Recommended action: {result.recommended_action}")
            print(f"Human review needed: {result.human_review_needed}")
        else:
            print("No ambiguities detected")
