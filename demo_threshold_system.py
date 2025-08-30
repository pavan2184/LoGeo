#!/usr/bin/env python3
"""
Demonstration of the Split Threshold System

This script demonstrates how the new threshold table system works with
different categories and escalation rules:

| Category                   | Confidence Threshold | Escalation Rule      |
|----------------------------|---------------------|---------------------|
| Legal / Compliance         | ≥ 0.90             | Below → human       |
| Safety / Health Protection | ≥ 0.85             | Below → human       |
| Business (non-binding)     | ≥ 0.70             | Below → auto OK     |
| Internal Analytics only    | ≥ 0.60             | Below → ignore      |
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from backend.glossary import get_glossary
from backend.enhanced_classifier import get_enhanced_classifier

def demonstrate_threshold_system():
    """Demonstrate the threshold system with various scenarios"""
    
    print("=" * 80)
    print("THRESHOLD TABLE SYSTEM DEMONSTRATION")
    print("=" * 80)
    
    # Get the glossary and classifier
    glossary = get_glossary()
    classifier = get_enhanced_classifier()
    
    # Display the threshold rules
    print("\n📋 THRESHOLD RULES CONFIGURATION:")
    print("-" * 50)
    
    threshold_rules = glossary.get_all_threshold_rules()
    for rule_name, rule in threshold_rules.items():
        print(f"\n🏷️  {rule.description}")
        print(f"   Rule Name: {rule_name}")
        print(f"   Threshold: {rule.confidence_threshold:.2f}")
        print(f"   Action if below threshold: {rule.below_threshold_action}")
        print(f"   Priority: {rule.priority}")
        print(f"   Categories: {', '.join(rule.categories)}")
    
    print("\n\n🧪 TESTING SCENARIOS:")
    print("=" * 50)
    
    # Test scenarios with different confidence levels and categories
    test_scenarios = [
        # Legal/Compliance scenarios (threshold: 0.90)
        {
            "title": "Utah Minor Curfew Implementation",
            "description": "Implement curfew restrictions for minors in Utah to comply with Utah Social Media Regulation Act",
            "expected_category": "minor_protection",
            "confidence_levels": [0.95, 0.85, 0.75]
        },
        {
            "title": "CSAM Detection System",
            "description": "Implement automated child sexual abuse material detection for NCMEC reporting requirements",
            "expected_category": "content_safety", 
            "confidence_levels": [0.92, 0.88, 0.82]
        },
        
        # Safety/Health scenarios (threshold: 0.85)
        {
            "title": "Content Moderation Enhancement",
            "description": "Enhance content moderation system for user safety and community standards enforcement",
            "expected_category": "user_safety",
            "confidence_levels": [0.90, 0.80, 0.70]
        },
        
        # Business scenarios (threshold: 0.70)
        {
            "title": "A/B Testing Framework",
            "description": "Implement A/B testing framework for user interface optimization in Canadian market",
            "expected_category": "market_testing",
            "confidence_levels": [0.85, 0.65, 0.55]
        },
        
        # Analytics scenarios (threshold: 0.60)
        {
            "title": "Performance Metrics Dashboard",
            "description": "Create internal dashboard for monitoring system performance and user analytics",
            "expected_category": "analytics",
            "confidence_levels": [0.75, 0.55, 0.45]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 SCENARIO {i}: {scenario['title']}")
        print(f"Description: {scenario['description']}")
        print(f"Expected Category: {scenario['expected_category']}")
        print("-" * 60)
        
        # Test with different confidence levels
        for confidence in scenario['confidence_levels']:
            print(f"\n🎯 Testing with confidence: {confidence:.2f}")
            
            # Evaluate using threshold system
            decision = glossary.evaluate_threshold(scenario['expected_category'], confidence)
            
            # Format the result
            status_icon = "✅" if decision.meets_threshold else "⚠️"
            action_icon = {
                "auto_approve": "🟢",
                "human_review": "🟡", 
                "ignore": "⚪"
            }.get(decision.escalation_action, "❓")
            
            print(f"   {status_icon} Threshold: {decision.threshold:.2f} | Result: {'PASS' if decision.meets_threshold else 'FAIL'}")
            print(f"   {action_icon} Action: {decision.escalation_action.upper()}")
            print(f"   📊 Priority: {decision.priority}")
            print(f"   💭 Reasoning: {decision.reasoning}")
    
    print("\n\n🔄 COMPLETE CLASSIFICATION TEST:")
    print("=" * 50)
    
    # Test complete classification pipeline
    test_feature = {
        "title": "California Age Verification System",
        "description": "Implement age verification system for California users to comply with California Age-Appropriate Design Code Act requirements for minor protection"
    }
    
    print(f"\nTesting complete classification pipeline:")
    print(f"Title: {test_feature['title']}")
    print(f"Description: {test_feature['description']}")
    
    try:
        result = classifier.classify(test_feature['title'], test_feature['description'])
        
        print(f"\n📊 CLASSIFICATION RESULTS:")
        print(f"   🎯 Overall Confidence: {result.overall_confidence:.3f}")
        feature_text = f"{test_feature['title']} {test_feature['description']}"
        feature_category = classifier.determine_feature_category(feature_text, result.standardized_entities)
        print(f"   🏷️  Feature Category: {feature_category}")
        print(f"   ⚖️  Needs Geo-Logic: {result.needs_geo_logic}")
        print(f"   🔄 Method Used: {result.method_used}")
        
        if result.threshold_decision:
            print(f"   📋 Threshold Rule: {result.threshold_decision.threshold_rule_name}")
            print(f"   🎚️  Threshold: {result.threshold_decision.threshold:.2f}")
            print(f"   ✅ Meets Threshold: {result.threshold_decision.meets_threshold}")
            print(f"   🎬 Final Action: {result.final_action}")
            print(f"   📊 Priority: {result.threshold_decision.priority}")
        
        print(f"   👤 Needs Human Review: {result.needs_human_review}")
        if result.needs_human_review:
            print(f"   💭 Review Reason: {result.human_review_reason}")
        
        print(f"   ⏱️  Processing Time: {result.processing_time_ms:.1f}ms")
        
    except Exception as e:
        print(f"❌ Error during classification: {e}")
    
    print("\n\n📚 THRESHOLD SYSTEM SUMMARY:")
    print("=" * 50)
    print("The threshold system now provides:")
    print("✅ Category-specific confidence thresholds")
    print("✅ Automated escalation rules (human, auto OK, ignore)")
    print("✅ Priority-based intervention")
    print("✅ Configurable via API endpoints")
    print("✅ Audit trail and reasoning")
    print("✅ Integration with classification pipeline")
    
    print("\n🔗 Available API endpoints:")
    print("   GET    /thresholds                     - Get all threshold rules")
    print("   GET    /thresholds/{rule_name}        - Get specific threshold rule") 
    print("   PUT    /thresholds/{rule_name}        - Update threshold rule")
    print("   POST   /thresholds/{rule_name}/evaluate - Evaluate confidence against rule")
    print("   GET    /thresholds/categories/mapping  - Get category to rule mapping")
    
    print("\n" + "=" * 80)

def test_api_simulation():
    """Simulate API calls to demonstrate threshold management"""
    
    print("\n🌐 API SIMULATION:")
    print("=" * 30)
    
    glossary = get_glossary()
    
    # Simulate getting all threshold rules
    print("\n📋 GET /thresholds - All threshold rules:")
    rules = glossary.get_all_threshold_rules()
    for rule_name, rule in rules.items():
        print(f"   {rule_name}: {rule.confidence_threshold:.2f} → {rule.below_threshold_action}")
    
    # Simulate category mapping
    print("\n🗺️  GET /thresholds/categories/mapping - Category mapping:")
    for rule_name, rule in rules.items():
        for category in rule.categories:
            print(f"   {category} → {rule_name} (threshold: {rule.confidence_threshold:.2f})")
    
    # Simulate threshold evaluation
    print("\n🎯 POST /thresholds/legal_compliance/evaluate - Evaluation examples:")
    test_cases = [
        ("minor_protection", 0.95),
        ("minor_protection", 0.85),
        ("business_feature", 0.65),
        ("analytics", 0.55)
    ]
    
    for category, confidence in test_cases:
        decision = glossary.evaluate_threshold(category, confidence)
        print(f"   {category} @ {confidence:.2f} → {decision.escalation_action} ({decision.priority} priority)")

if __name__ == "__main__":
    try:
        demonstrate_threshold_system()
        test_api_simulation()
        
        print(f"\n🎉 Threshold system demonstration completed successfully!")
        print(f"💡 The pipeline now knows upfront what cutoff applies based on feature categories.")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
