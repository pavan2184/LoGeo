"""
Confidence Scoring System for Geo-Compliance Classification

This module implements the standardized confidence scoring rubric:
- 0.0-0.3: Low confidence (LLM unsure, requires human review)
- 0.31-0.7: Medium confidence (possible match, requires cross-check)
- 0.71-1.0: High confidence (strong evidence, can proceed)

Provides weighted scoring logic and confidence interpretation utilities.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Standardized confidence levels with clear thresholds"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"

@dataclass
class ConfidenceBreakdown:
    """Detailed confidence score breakdown"""
    llm_confidence: float
    regex_ner_confidence: float
    entity_confidence: float
    cross_validation_confidence: float
    final_confidence: float
    confidence_level: ConfidenceLevel
    confidence_factors: Dict[str, float]
    recommendations: List[str]

@dataclass
class WeightedScoreConfig:
    """Configuration for weighted scoring between different methods"""
    llm_weight: float = 0.7
    regex_ner_weight: float = 0.3
    entity_quality_factor: float = 0.2
    cross_validation_factor: float = 0.15
    diversity_bonus_cap: float = 0.1

class ConfidenceScorer:
    """
    Standardized confidence scoring system with clear rubric and weighted logic.
    
    Confidence Scale Definition:
    - 0.0-0.3 = Low (LLM unsure, high uncertainty)
    - 0.31-0.7 = Medium (possible match, requires cross-validation)  
    - 0.71-1.0 = High (strong evidence, high certainty)
    """
    
    # Official confidence thresholds
    CONFIDENCE_THRESHOLDS = {
        "low_upper": 0.30,
        "medium_lower": 0.31,
        "medium_upper": 0.70,
        "high_lower": 0.71
    }
    
    def __init__(self, weight_config: Optional[WeightedScoreConfig] = None):
        self.weights = weight_config or WeightedScoreConfig()
        
    def classify_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Classify confidence score into standard levels"""
        if confidence <= self.CONFIDENCE_THRESHOLDS["low_upper"]:
            return ConfidenceLevel.LOW
        elif confidence <= self.CONFIDENCE_THRESHOLDS["medium_upper"]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.HIGH
    
    def get_confidence_description(self, confidence: float) -> str:
        """Get human-readable description of confidence level"""
        level = self.classify_confidence_level(confidence)
        
        descriptions = {
            ConfidenceLevel.LOW: f"Low confidence ({confidence:.3f}) - LLM unsure, requires human review",
            ConfidenceLevel.MEDIUM: f"Medium confidence ({confidence:.3f}) - Possible match, requires cross-check",
            ConfidenceLevel.HIGH: f"High confidence ({confidence:.3f}) - Strong evidence, can proceed"
        }
        
        return descriptions[level]
    
    def get_confidence_recommendations(self, confidence: float, context: Dict[str, Any] = None) -> List[str]:
        """Get specific recommendations based on confidence level"""
        level = self.classify_confidence_level(confidence)
        context = context or {}
        
        base_recommendations = {
            ConfidenceLevel.LOW: [
                "Flag for immediate human review",
                "Do not auto-approve any actions",
                "Collect additional context or clarification",
                "Consider manual classification override"
            ],
            ConfidenceLevel.MEDIUM: [
                "Perform additional cross-validation checks",
                "Review entity extraction quality",
                "Check for regulatory pattern matches",
                "Consider elevated review threshold"
            ],
            ConfidenceLevel.HIGH: [
                "Proceed with automated classification",
                "Log decision for audit trail",
                "Apply standard compliance rules",
                "Monitor for feedback patterns"
            ]
        }
        
        recommendations = base_recommendations[level].copy()
        
        # Add context-specific recommendations
        if context.get("has_ambiguous_entities"):
            recommendations.append("Review ambiguous entity mappings")
        
        if context.get("regulatory_conflict"):
            recommendations.append("Resolve regulatory requirement conflicts")
            
        if context.get("location_uncertainty"):
            recommendations.append("Clarify geographic scope and jurisdiction")
            
        return recommendations
    
    def calculate_weighted_confidence(self, 
                                    llm_score: float,
                                    regex_ner_score: float,
                                    entity_quality: float = 0.5,
                                    cross_validation_score: float = 0.5,
                                    diversity_factors: Dict[str, bool] = None) -> ConfidenceBreakdown:
        """
        Calculate final confidence using weighted scoring methodology.
        
        Args:
            llm_score: Primary LLM confidence (0-1)
            regex_ner_score: Secondary regex/NER confidence (0-1)
            entity_quality: Quality of extracted entities (0-1)
            cross_validation_score: Cross-validation between methods (0-1)
            diversity_factors: Dict of boolean factors (has_locations, has_ages, etc.)
        
        Returns:
            ConfidenceBreakdown with detailed scoring analysis
        """
        diversity_factors = diversity_factors or {}
        
        # Base weighted score (70% LLM + 30% Regex/NER)
        base_confidence = (llm_score * self.weights.llm_weight + 
                          regex_ner_score * self.weights.regex_ner_weight)
        
        # Entity quality adjustment (±20% based on entity extraction quality)
        entity_adjustment = (entity_quality - 0.5) * self.weights.entity_quality_factor
        
        # Cross-validation boost/penalty
        cross_val_adjustment = (cross_validation_score - 0.5) * self.weights.cross_validation_factor
        
        # Diversity bonus for multiple signal types
        diversity_count = sum(1 for factor in diversity_factors.values() if factor)
        diversity_bonus = min(diversity_count * 0.05, self.weights.diversity_bonus_cap)
        
        # Calculate final confidence
        final_confidence = base_confidence + entity_adjustment + cross_val_adjustment + diversity_bonus
        final_confidence = max(0.0, min(1.0, final_confidence))  # Clamp to [0,1]
        
        # Determine confidence level and recommendations
        confidence_level = self.classify_confidence_level(final_confidence)
        recommendations = self.get_confidence_recommendations(final_confidence, {
            "has_ambiguous_entities": entity_quality < 0.7,
            "regulatory_conflict": cross_validation_score < 0.6,
            "location_uncertainty": not diversity_factors.get("has_locations", False)
        })
        
        # Detailed factor analysis
        confidence_factors = {
            "base_weighted": base_confidence,
            "llm_component": llm_score * self.weights.llm_weight,
            "regex_ner_component": regex_ner_score * self.weights.regex_ner_weight,
            "entity_adjustment": entity_adjustment,
            "cross_validation_adjustment": cross_val_adjustment,
            "diversity_bonus": diversity_bonus,
            "final_confidence": final_confidence
        }
        
        return ConfidenceBreakdown(
            llm_confidence=llm_score,
            regex_ner_confidence=regex_ner_score,
            entity_confidence=entity_quality,
            cross_validation_confidence=cross_validation_score,
            final_confidence=final_confidence,
            confidence_level=confidence_level,
            confidence_factors=confidence_factors,
            recommendations=recommendations
        )
    
    def validate_confidence_alignment(self, 
                                    llm_result: float,
                                    regex_result: float,
                                    threshold: float = 0.3) -> Tuple[bool, str, float]:
        """
        Validate alignment between LLM and regex/NER results.
        
        Returns:
            (is_aligned, explanation, alignment_score)
        """
        alignment_score = 1.0 - abs(llm_result - regex_result)
        is_aligned = alignment_score >= threshold
        
        if is_aligned:
            explanation = f"Good alignment between LLM ({llm_result:.3f}) and regex/NER ({regex_result:.3f})"
        else:
            explanation = f"Poor alignment: LLM ({llm_result:.3f}) vs regex/NER ({regex_result:.3f}) - requires review"
            
        return is_aligned, explanation, alignment_score
    
    def suggest_confidence_improvements(self, breakdown: ConfidenceBreakdown) -> List[str]:
        """Suggest specific improvements based on confidence breakdown"""
        suggestions = []
        factors = breakdown.confidence_factors
        
        if factors["llm_component"] < 0.5:
            suggestions.append("Improve LLM prompt engineering or provide more regulatory context")
        
        if factors["regex_ner_component"] < 0.2:
            suggestions.append("Enhance regex patterns and NER model training")
            
        if factors["entity_adjustment"] < 0:
            suggestions.append("Improve entity extraction quality through glossary updates")
            
        if factors["cross_validation_adjustment"] < 0:
            suggestions.append("Review cross-validation logic and alignment criteria")
            
        if factors["diversity_bonus"] == 0:
            suggestions.append("Extract more diverse entity types for better signal coverage")
            
        return suggestions
    
    def export_confidence_metrics(self, breakdown: ConfidenceBreakdown) -> Dict[str, Any]:
        """Export confidence metrics for monitoring and analytics"""
        return {
            "confidence_score": breakdown.final_confidence,
            "confidence_level": breakdown.confidence_level.value,
            "confidence_category": self.get_confidence_description(breakdown.final_confidence),
            "component_scores": {
                "llm": breakdown.llm_confidence,
                "regex_ner": breakdown.regex_ner_confidence,
                "entity_quality": breakdown.entity_confidence,
                "cross_validation": breakdown.cross_validation_confidence
            },
            "scoring_factors": breakdown.confidence_factors,
            "recommendations": breakdown.recommendations,
            "rubric_thresholds": self.CONFIDENCE_THRESHOLDS
        }

# Global confidence scorer instance
_confidence_scorer_instance = None

def get_confidence_scorer() -> ConfidenceScorer:
    """Get singleton confidence scorer instance"""
    global _confidence_scorer_instance
    if _confidence_scorer_instance is None:
        _confidence_scorer_instance = ConfidenceScorer()
    return _confidence_scorer_instance

if __name__ == "__main__":
    # Test the confidence scoring system
    scorer = ConfidenceScorer()
    
    # Test cases representing different confidence scenarios
    test_cases = [
        {
            "name": "High Confidence Case",
            "llm_score": 0.95,
            "regex_ner_score": 0.88,
            "entity_quality": 0.90,
            "cross_validation": 0.85,
            "diversity": {"has_locations": True, "has_ages": True, "has_terminology": True}
        },
        {
            "name": "Medium Confidence Case", 
            "llm_score": 0.65,
            "regex_ner_score": 0.70,
            "entity_quality": 0.60,
            "cross_validation": 0.55,
            "diversity": {"has_locations": True, "has_ages": False, "has_terminology": True}
        },
        {
            "name": "Low Confidence Case",
            "llm_score": 0.25,
            "regex_ner_score": 0.30,
            "entity_quality": 0.40,
            "cross_validation": 0.20,
            "diversity": {"has_locations": False, "has_ages": False, "has_terminology": True}
        }
    ]
    
    for case in test_cases:
        print(f"\n=== {case['name']} ===")
        breakdown = scorer.calculate_weighted_confidence(
            case['llm_score'],
            case['regex_ner_score'], 
            case['entity_quality'],
            case['cross_validation'],
            case['diversity']
        )
        
        print(f"Final Confidence: {breakdown.final_confidence:.3f}")
        print(f"Confidence Level: {breakdown.confidence_level.value}")
        print(f"Description: {scorer.get_confidence_description(breakdown.final_confidence)}")
        print(f"Key Recommendations: {breakdown.recommendations[:2]}")
        
        # Test alignment validation
        aligned, explanation, alignment_score = scorer.validate_confidence_alignment(
            case['llm_score'], case['regex_ner_score']
        )
        print(f"Alignment: {aligned} ({alignment_score:.3f}) - {explanation}")
