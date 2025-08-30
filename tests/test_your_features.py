#!/usr/bin/env python3
"""
Test Your Own Features with the Enhanced Threshold System

Input your feature descriptions and see how the system categorizes them
and applies category-specific thresholds.
"""

from backend.enhanced_decision_engine import EnhancedDecisionEngine

def test_custom_feature():
    """Test a custom feature with user input"""
    
    print("🎯 TEST YOUR OWN FEATURES")
    print("=" * 50)
    print("Enter a feature description to test the threshold system")
    print("Examples:")
    print("• 'Age gate for users under 16 in EU'")
    print("• 'A/B test new UI in Canada'") 
    print("• 'Performance optimization for analytics'")
    print("• 'VAT collection from EU sellers'")
    print()
    
    # Get user input
    title = input("Feature Title: ").strip()
    description = input("Feature Description: ").strip()
    
    if not title or not description:
        print("❌ Please provide both title and description")
        return
    
    # Simulate LLM output (you can adjust these values)
    print("\n🔧 Simulate LLM Output:")
    confidence = float(input("LLM Confidence (0.0-1.0): ") or "0.75")
    flag = input("LLM Flag (NeedsGeoLogic/NoGeoLogic/Ambiguous): ") or "Ambiguous"
    
    # Simulate rules matched
    print("\n🔍 Rules Matched (comma-separated, or press Enter for none):")
    rules_input = input("Rules: ").strip()
    rules_matched = [r.strip() for r in rules_input.split(",")] if rules_input else []
    
    # Create simulated LLM output
    llm_output = {
        "flag": flag,
        "confidence": confidence,
        "reasoning": f"Simulated output for: {title}",
        "suggested_jurisdictions": [],
        "evidence_passage_ids": []
    }
    
    # Run the enhanced decision engine
    print("\n" + "="*50)
    print("🧠 ENHANCED DECISION ENGINE RESULTS")
    print("="*50)
    
    engine = EnhancedDecisionEngine()
    
    result = engine.make_decision(
        feature_text=f"{title}: {description}",
        llm_output=llm_output,
        rules_matched=rules_matched,
        rule_fired=len(rules_matched) > 0
    )
    
    # Display results
    print(f"📋 Feature: {title}")
    print(f"📝 Description: {description}")
    print(f"🏷️  LLM Flag: {flag}")
    print(f"📊 LLM Confidence: {confidence:.2f}")
    print(f"🔧 Rules Matched: {rules_matched}")
    print()
    
    print("🎯 CATEGORY ANALYSIS:")
    print(f"   Categories Detected: {result.categories_detected}")
    if result.categories_detected:
        threshold, escalation = engine.get_applicable_threshold(result.categories_detected)
        print(f"   Applicable Threshold: {threshold:.2f}")
        print(f"   Escalation Rule: {escalation.value}")
    print()
    
    print("📋 FINAL DECISION:")
    print(f"   Final Flag: {result.final_flag}")
    print(f"   Final Confidence: {result.confidence:.2f}")
    print(f"   Review Required: {result.review_required}")
    print(f"   Review Priority: {result.review_priority}")
    print()
    
    if result.escalation_required:
        print("⚠️  ESCALATION REQUIRED:")
        print(f"   Reason: {result.escalation_reason}")
        print(f"   Threshold Violations: {result.threshold_violations}")
    
    print("\n" + "="*50)

def run_predefined_tests():
    """Run some predefined test cases"""
    
    print("🧪 PREDEFINED TEST CASES")
    print("=" * 50)
    
    test_cases = [
        {
            "title": "High Risk - GDPR Compliance",
            "description": "Age verification for EU users under 16 to comply with GDPR Article 8",
            "confidence": 0.88,
            "flag": "NeedsGeoLogic",
            "rules": []
        },
        {
            "title": "Medium Risk - Child Protection", 
            "description": "Parental controls for users under 13 in US markets",
            "confidence": 0.82,
            "flag": "NeedsGeoLogic",
            "rules": ["child_protection"]
        },
        {
            "title": "Low Risk - Business Analytics",
            "description": "A/B test new UI design in Canada for user engagement",
            "confidence": 0.75,
            "flag": "NoGeoLogic", 
            "rules": []
        },
        {
            "title": "Very Low Risk - Internal Tool",
            "description": "Performance optimization for thumbnail caching",
            "confidence": 0.65,
            "flag": "NoGeoLogic",
            "rules": []
        }
    ]
    
    engine = EnhancedDecisionEngine()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['title']}")
        print("-" * 40)
        
        llm_output = {
            "flag": test_case["flag"],
            "confidence": test_case["confidence"],
            "reasoning": f"Test case {i}",
            "suggested_jurisdictions": [],
            "evidence_passage_ids": []
        }
        
        result = engine.make_decision(
            feature_text=f"{test_case['title']}: {test_case['description']}",
            llm_output=llm_output,
            rules_matched=test_case["rules"],
            rule_fired=len(test_case["rules"]) > 0
        )
        
        print(f"Description: {test_case['description']}")
        print(f"LLM Confidence: {test_case['confidence']:.2f}")
        print(f"Categories: {result.categories_detected}")
        if result.categories_detected:
            threshold, _ = engine.get_applicable_threshold(result.categories_detected)
            print(f"Threshold: {threshold:.2f}")
        print(f"Final Flag: {result.final_flag}")
        print(f"Review Required: {result.review_required}")
        print(f"Priority: {result.review_priority}")

def main():
    """Main menu for testing options"""
    
    while True:
        print("\n🎯 ENHANCED THRESHOLD SYSTEM TESTING")
        print("=" * 50)
        print("1. Test your own feature")
        print("2. Run predefined test cases") 
        print("3. View threshold configuration")
        print("4. Exit")
        print()
        
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == "1":
            test_custom_feature()
        elif choice == "2":
            run_predefined_tests()
        elif choice == "3":
            engine = EnhancedDecisionEngine()
            print("\n📊 THRESHOLD CONFIGURATION:")
            print("=" * 40)
            summary = engine.get_threshold_summary()
            for category, config in summary.items():
                print(f"• {category.replace('_', ' ').title()}: {config['threshold']:.2f} → {config['escalation']}")
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 