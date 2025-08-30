#!/usr/bin/env python3
"""
Enhanced Decision Engine with Category-Specific Thresholds

This module implements the threshold-based decision system described in the requirements:
1. Different confidence thresholds per category (legal=0.90, safety=0.85, business=0.70, etc.)
2. Automatic detection flow with category matching
3. Hybrid handling using strictest threshold when multiple categories apply
4. Escalation rules based on threshold violations
"""

import json
import os
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

class EscalationRule(Enum):
    HUMAN_REVIEW = "human_review"
    AUTO_OK = "auto_ok"
    IGNORE = "ignore"

@dataclass
class CategoryThreshold:
    """Represents a category with its threshold and escalation rule"""
    name: str
    confidence_threshold: float
    escalation_rule: EscalationRule
    description: str
    examples: List[str]

@dataclass
class DecisionResult:
    """Result of the enhanced decision process"""
    final_flag: str
    confidence: float
    reasoning: str
    categories_detected: List[str]
    threshold_violations: List[str]
    escalation_required: bool
    escalation_rule: EscalationRule
    escalation_reason: str
    review_required: bool
    review_priority: str

class EnhancedDecisionEngine:
    """Enhanced decision engine with category-specific thresholds"""
    
    def __init__(self, threshold_config_path: str = "threshold_config.json"):
        self.threshold_config = self._load_threshold_config(threshold_config_path)
        self.categories = self._build_category_map()
        
    def _load_threshold_config(self, config_path: str) -> Dict[str, Any]:
        """Load threshold configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {config_path} not found, using default thresholds")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Fallback default configuration"""
        return {
            "thresholds": {
                "legal_compliance": {"confidence_threshold": 0.90, "escalation_rule": "human_review"},
                "safety_health_protection": {"confidence_threshold": 0.85, "escalation_rule": "human_review"},
                "business_analytics": {"confidence_threshold": 0.70, "escalation_rule": "auto_ok"},
                "internal_features": {"confidence_threshold": 0.60, "escalation_rule": "ignore"}
            }
        }
    
    def _build_category_map(self) -> Dict[str, CategoryThreshold]:
        """Build category objects from configuration"""
        categories = {}
        for name, config in self.threshold_config["thresholds"].items():
            categories[name] = CategoryThreshold(
                name=name,
                confidence_threshold=config["confidence_threshold"],
                escalation_rule=EscalationRule(config["escalation_rule"]),
                description=config.get("description", ""),
                examples=config.get("examples", [])
            )
        return categories
    
    def detect_categories(self, feature_text: str, llm_output: Dict[str, Any], 
                         rules_matched: List[str]) -> List[str]:
        """
        Detect which categories apply to this feature based on:
        1. LLM output (jurisdictions, evidence)
        2. Rules matched (regex patterns)
        3. Feature text content
        """
        detected_categories = set()
        
        # Check rules matched
        if "child_protection" in rules_matched:
            detected_categories.add("safety_health_protection")
        if "data_residency" in rules_matched:
            detected_categories.add("data_residency")
        if "tax_shop" in rules_matched:
            detected_categories.add("tax_compliance")
        
        # Check LLM output for legal terms
        evidence_ids = llm_output.get("evidence_passage_ids", [])
        jurisdictions = llm_output.get("suggested_jurisdictions", [])
        
        # Look for legal compliance indicators
        legal_indicators = ["GDPR", "COPPA", "DSA", "CCPA", "HIPAA"]
        if any(indicator in str(jurisdictions) for indicator in legal_indicators):
            detected_categories.add("legal_compliance")
        
        # Check for business/analytics terms
        business_terms = ["A/B test", "experiment", "analytics", "segmentation", "pilot"]
        if any(term.lower() in feature_text.lower() for term in business_terms):
            detected_categories.add("business_analytics")
        
        # Check for internal/performance terms
        internal_terms = ["performance", "cache", "optimization", "internal"]
        if any(term.lower() in feature_text.lower() for term in internal_terms):
            detected_categories.add("internal_features")
        
        return list(detected_categories)
    
    def get_applicable_threshold(self, categories: List[str]) -> Tuple[float, EscalationRule]:
        """
        Get the applicable threshold and escalation rule.
        For multiple categories, use the strictest (highest) threshold.
        """
        if not categories:
            # Default to business analytics if no categories detected
            return (0.70, EscalationRule.AUTO_OK)
        
        # Find the category with the highest threshold (strictest)
        strictest_category = max(categories, key=lambda c: self.categories[c].confidence_threshold)
        category_obj = self.categories[strictest_category]
        
        return (category_obj.confidence_threshold, category_obj.escalation_rule)
    
    def make_decision(self, feature_text: str, llm_output: Dict[str, Any], 
                      rules_matched: List[str], rule_fired: bool) -> DecisionResult:
        """
        Enhanced decision making with category-specific thresholds
        """
        # Step 1: Apply deterministic rules first (override everything)
        if rule_fired:
            return DecisionResult(
                final_flag="NeedsGeoLogic",
                confidence=0.95,
                reasoning=f"Deterministic rule(s) matched: {', '.join(rules_matched)}",
                categories_detected=["deterministic_override"],
                threshold_violations=[],
                escalation_required=False,
                escalation_rule=EscalationRule.AUTO_OK,
                escalation_reason="Rules fired - automatic override",
                review_required=False,
                review_priority="low"
            )
        
        # Step 2: Detect applicable categories
        categories = self.detect_categories(feature_text, llm_output, rules_matched)
        
        # Step 3: Get applicable threshold and escalation rule
        threshold, escalation_rule = self.get_applicable_threshold(categories)
        
        # Step 4: Get LLM confidence and flag
        llm_confidence = float(llm_output.get("confidence", 0.6))
        llm_flag = llm_output.get("flag", "Ambiguous")
        
        # Step 5: Apply category-specific threshold logic
        threshold_violations = []
        escalation_required = False
        escalation_reason = ""
        
        if llm_confidence < threshold:
            threshold_violations.append(f"LLM confidence {llm_confidence:.2f} < {threshold:.2f} for categories: {categories}")
            escalation_required = True
            escalation_reason = f"Confidence {llm_confidence:.2f} below threshold {threshold:.2f} for {', '.join(categories)}"
        
        # Step 6: Determine final flag and review requirements
        if llm_confidence >= threshold:
            final_flag = llm_flag
            final_confidence = llm_confidence
            review_required = False
        else:
            # Below threshold - mark as ambiguous and require review
            final_flag = "Ambiguous"
            final_confidence = llm_confidence
            review_required = True
        
        # Step 7: Determine review priority based on escalation rule
        if escalation_rule == EscalationRule.HUMAN_REVIEW:
            review_priority = "high"
        elif escalation_rule == EscalationRule.AUTO_OK:
            review_priority = "medium"
        else:
            review_priority = "low"
        
        return DecisionResult(
            final_flag=final_flag,
            confidence=final_confidence,
            reasoning=llm_output.get("reasoning", ""),
            categories_detected=categories,
            threshold_violations=threshold_violations,
            escalation_required=escalation_required,
            escalation_rule=escalation_rule,
            escalation_reason=escalation_reason,
            review_required=review_required,
            review_priority=review_priority
        )
    
    def get_threshold_summary(self) -> Dict[str, Any]:
        """Get a summary of all thresholds for monitoring/reporting"""
        summary = {}
        for name, category in self.categories.items():
            summary[name] = {
                "threshold": category.confidence_threshold,
                "escalation": category.escalation_rule.value,
                "description": category.description
            }
        return summary

# Example usage and testing
if __name__ == "__main__":
    engine = EnhancedDecisionEngine()
    
    # Test case 1: High-risk legal compliance
    test_llm_output = {
        "flag": "NeedsGeoLogic",
        "confidence": 0.88,
        "reasoning": "GDPR compliance required for EU users",
        "suggested_jurisdictions": ["European Union"],
        "evidence_passage_ids": ["EV1"]
    }
    
    result = engine.make_decision(
        feature_text="GDPR compliance for EU users under 16",
        llm_output=test_llm_output,
        rules_matched=[],
        rule_fired=False
    )
    
    print("Test Case 1: GDPR Compliance")
    print(f"Categories: {result.categories_detected}")
    print(f"Threshold: {engine.get_applicable_threshold(result.categories_detected)[0]}")
    print(f"LLM Confidence: {test_llm_output['confidence']}")
    print(f"Final Flag: {result.final_flag}")
    print(f"Review Required: {result.review_required}")
    print(f"Escalation Reason: {result.escalation_reason}")
    print()
    
    # Test case 2: Low-risk business analytics
    test_llm_output2 = {
        "flag": "NoGeoLogic", 
        "confidence": 0.75,
        "reasoning": "A/B testing for user engagement",
        "suggested_jurisdictions": [],
        "evidence_passage_ids": []
    }
    
    result2 = engine.make_decision(
        feature_text="A/B test new UI design in Canada for user engagement",
        llm_output=test_llm_output2,
        rules_matched=[],
        rule_fired=False
    )
    
    print("Test Case 2: Business Analytics")
    print(f"Categories: {result2.categories_detected}")
    print(f"Threshold: {engine.get_applicable_threshold(result2.categories_detected)[0]}")
    print(f"LLM Confidence: {test_llm_output2['confidence']}")
    print(f"Final Flag: {result2.final_flag}")
    print(f"Review Required: {result2.review_required}")
    print(f"Escalation Reason: {result2.escalation_reason}")
    print()
    
    print("Threshold Summary:")
    print(json.dumps(engine.get_threshold_summary(), indent=2)) 