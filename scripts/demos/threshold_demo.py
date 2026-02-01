#!/usr/bin/env python3
"""
Threshold System Demo - Shows Category-Specific Thresholds in Action

This demo illustrates how different confidence thresholds apply to different categories:
- Legal/Compliance: 0.90 threshold (super strict)
- Safety/Health: 0.85 threshold (strict)  
- Business/Analytics: 0.70 threshold (moderate)
- Internal: 0.60 threshold (low risk)
"""

from backend.enhanced_decision_engine import EnhancedDecisionEngine

def run_threshold_demo():
    """Demonstrate the threshold system with various test cases"""
    
    print("🎯 ENHANCED THRESHOLD SYSTEM DEMO")
    print("=" * 60)
    print("Different categories have different confidence thresholds:")
    print("• Legal/Compliance: 0.90 (super strict)")
    print("• Safety/Health: 0.85 (strict)")
    print("• Business/Analytics: 0.70 (moderate)")
    print("• Internal: 0.60 (low risk)")
    print()
    
    engine = EnhancedDecisionEngine()
    
    # Test Case 1: High-risk Legal Compliance (GDPR)
    print("🧪 TEST CASE 1: GDPR Compliance (High Risk)")
    print("-" * 40)
    
    llm_output = {
        "flag": "NeedsGeoLogic",
        "confidence": 0.88,  # Below 0.90 threshold
        "reasoning": "GDPR compliance required for EU users under 16",
        "suggested_jurisdictions": ["European Union"],
        "evidence_passage_ids": ["EV1", "EV2"]
    }
    
    result = engine.make_decision(
        feature_text="Implement age verification for EU users under 16 to comply with GDPR Article 8",
        llm_output=llm_output,
        rules_matched=[],
        rule_fired=False
    )
    
    print(f"Feature: GDPR age verification for EU minors")
    print(f"LLM Confidence: {llm_output['confidence']:.2f}")
    print(f"Categories Detected: {result.categories_detected}")
    print(f"Applicable Threshold: {engine.get_applicable_threshold(result.categories_detected)[0]:.2f}")
    print(f"Final Flag: {result.final_flag}")
    print(f"Review Required: {result.review_required}")
    print(f"Escalation Reason: {result.escalation_reason}")
    print(f"Review Priority: {result.review_priority}")
    print()
    
    # Test Case 2: Moderate Risk Safety (Child Protection)
    print("🧪 TEST CASE 2: Child Protection (Moderate Risk)")
    print("-" * 40)
    
    llm_output2 = {
        "flag": "NeedsGeoLogic",
        "confidence": 0.82,  # Below 0.85 threshold
        "reasoning": "Child protection features may require geo-logic",
        "suggested_jurisdictions": ["United States"],
        "evidence_passage_ids": ["EV2"]
    }
    
    result2 = engine.make_decision(
        feature_text="Add parental controls for users under 13 in US markets",
        llm_output=llm_output2,
        rules_matched=["child_protection"],
        rule_fired=False
    )
    
    print(f"Feature: Parental controls for US minors")
    print(f"LLM Confidence: {llm_output2['confidence']:.2f}")
    print(f"Categories Detected: {result2.categories_detected}")
    print(f"Applicable Threshold: {engine.get_applicable_threshold(result2.categories_detected)[0]:.2f}")
    print(f"Final Flag: {result2.final_flag}")
    print(f"Review Required: {result2.review_required}")
    print(f"Escalation Reason: {result2.escalation_reason}")
    print(f"Review Priority: {result2.review_priority}")
    print()
    
    # Test Case 3: Low Risk Business Analytics
    print("🧪 TEST CASE 3: Business Analytics (Low Risk)")
    print("-" * 40)
    
    llm_output3 = {
        "flag": "NoGeoLogic",
        "confidence": 0.75,  # Above 0.70 threshold
        "reasoning": "A/B testing for user engagement optimization",
        "suggested_jurisdictions": [],
        "evidence_passage_ids": []
    }
    
    result3 = engine.make_decision(
        feature_text="A/B test new UI design in Canada for user engagement optimization",
        llm_output=llm_output3,
        rules_matched=[],
        rule_fired=False
    )
    
    print(f"Feature: A/B test UI design in Canada")
    print(f"LLM Confidence: {llm_output3['confidence']:.2f}")
    print(f"Categories Detected: {result3.categories_detected}")
    print(f"Applicable Threshold: {engine.get_applicable_threshold(result3.categories_detected)[0]:.2f}")
    print(f"Final Flag: {result3.final_flag}")
    print(f"Review Required: {result3.review_required}")
    print(f"Escalation Reason: {result3.escalation_reason}")
    print(f"Review Priority: {result3.review_priority}")
    print()
    
    # Test Case 4: Very Low Risk Internal Feature
    print("🧪 TEST CASE 4: Internal Feature (Very Low Risk)")
    print("-" * 40)
    
    llm_output4 = {
        "flag": "NoGeoLogic",
        "confidence": 0.65,  # Above 0.60 threshold
        "reasoning": "Performance optimization for internal use",
        "suggested_jurisdictions": [],
        "evidence_passage_ids": []
    }
    
    result4 = engine.make_decision(
        feature_text="Optimize thumbnail caching performance for internal analytics",
        llm_output=llm_output4,
        rules_matched=[],
        rule_fired=False
    )
    
    print(f"Feature: Performance optimization for analytics")
    print(f"LLM Confidence: {llm_output4['confidence']:.2f}")
    print(f"Categories Detected: {result4.categories_detected}")
    print(f"Applicable Threshold: {engine.get_applicable_threshold(result4.categories_detected)[0]:.2f}")
    print(f"Final Flag: {result4.final_flag}")
    print(f"Review Required: {result4.review_required}")
    print(f"Escalation Reason: {result4.escalation_reason}")
    print(f"Review Priority: {result4.review_priority}")
    print()
    
    # Test Case 5: Hybrid Case (Multiple Categories)
    print("🧪 TEST CASE 5: Hybrid Case (Multiple Categories)")
    print("-" * 40)
    
    llm_output5 = {
        "flag": "NeedsGeoLogic",
        "confidence": 0.86,  # Below 0.88 threshold (strictest of multiple categories)
        "reasoning": "Combines child protection with data residency requirements",
        "suggested_jurisdictions": ["European Union"],
        "evidence_passage_ids": ["EV1", "EV4"]
    }
    
    result5 = engine.make_decision(
        feature_text="Store EU minor user data locally with enhanced parental controls",
        llm_output=llm_output5,
        rules_matched=["child_protection", "data_residency"],
        rule_fired=False
    )
    
    print(f"Feature: EU minor data storage + parental controls")
    print(f"LLM Confidence: {llm_output5['confidence']:.2f}")
    print(f"Categories Detected: {result5.categories_detected}")
    print(f"Applicable Threshold: {engine.get_applicable_threshold(result5.categories_detected)[0]:.2f}")
    print(f"Final Flag: {result5.final_flag}")
    print(f"Review Required: {result5.review_required}")
    print(f"Escalation Reason: {result5.escalation_reason}")
    print(f"Review Priority: {result5.review_priority}")
    print()
    
    # Summary
    print("📊 THRESHOLD SYSTEM SUMMARY")
    print("=" * 60)
    print("The system automatically:")
    print("1. Detects applicable categories for each feature")
    print("2. Applies the strictest threshold when multiple categories apply")
    print("3. Flags for human review when confidence is below threshold")
    print("4. Provides escalation rules based on risk level")
    print()
    
    threshold_summary = engine.get_threshold_summary()
    for category, config in threshold_summary.items():
        print(f"• {category.replace('_', ' ').title()}: {config['threshold']:.2f} → {config['escalation']}")

if __name__ == "__main__":
    run_threshold_demo() 