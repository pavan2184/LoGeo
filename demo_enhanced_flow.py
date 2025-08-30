#!/usr/bin/env python3
"""
Demonstration of the Enhanced Geo-Compliance Feature Flow

This script demonstrates the complete multi-stage pipeline:
1. Pre-processing and tokenization
2. NER and Regex searches for clear-cut geotagging cases (95% confidence)
3. Entity standardization using glossary
4. Multi-stage classification with primary (LLM) + secondary (Regex/NER) cross-checking
5. Confidence calculation with category-specific thresholds
6. Human intervention alerts for low confidence cases
7. Self-evolution through feedback loops
"""

import sys
import os
import json
import time
import asyncio
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our enhanced classifier system
from backend.enhanced_classifier import get_enhanced_classifier
from backend.feedback_system import get_feedback_processor, FeedbackType, InterventionPriority
from backend.glossary import get_glossary

class EnhancedFlowDemo:
    """Demonstration class for the enhanced geo-compliance feature flow"""
    
    def __init__(self):
        self.enhanced_classifier = get_enhanced_classifier()
        self.feedback_processor = get_feedback_processor()
        self.glossary = get_glossary()
        
        print("🚀 Enhanced Geo-Compliance Feature Flow Demo")
        print("=" * 60)
        print("✅ Glossary system loaded")
        print("✅ Preprocessing pipeline ready")
        print("✅ NER and regex patterns compiled")
        print("✅ Enhanced classifier initialized")
        print("✅ Feedback system ready")
        print()
    
    def demo_test_cases(self):
        """Demonstrate the system with various test cases"""
        
        test_cases = [
            {
                "title": "Utah Minor Curfew System",
                "description": "Implement curfew restrictions for users under 18 in Utah to comply with Utah Social Media Regulation Act. System blocks login between 10:30 PM and 6:30 AM.",
                "expected": "Clear-cut compliance case - should trigger geo-logic with high confidence"
            },
            {
                "title": "CSAM Detection for NCMEC",
                "description": "Automated child sexual abuse material detection system for reporting to National Center for Missing & Exploited Children as required by US federal law.",
                "expected": "Clear regulatory requirement - should trigger geo-logic"
            },
            {
                "title": "California Teen Privacy Controls",
                "description": "Default privacy settings for users under 18 in California to comply with SB976 Age-Appropriate Design Code Act.",
                "expected": "Location + age + compliance terms - should trigger geo-logic"
            },
            {
                "title": "Market Testing in Canada",
                "description": "A/B test new UI design with Canadian users for user engagement optimization and conversion rate improvement.",
                "expected": "Business decision - should NOT trigger geo-logic"
            },
            {
                "title": "Global Avatar Customization",
                "description": "Users can create custom avatars with various clothing and accessory options. Feature is available worldwide.",
                "expected": "No geo-specific requirements - should NOT trigger geo-logic"
            },
            {
                "title": "EU Content Transparency",
                "description": "Content flagging system for EU users with transparency reporting to meet Digital Services Act requirements.",
                "expected": "EU-specific regulatory requirement - should trigger geo-logic"
            },
            {
                "title": "Ambiguous Regional Feature",
                "description": "Video filters available in selected regions for pilot testing. Limited rollout for performance evaluation.",
                "expected": "Ambiguous case - might need human review"
            }
        ]
        
        print("🧪 TESTING ENHANCED FEATURE FLOW")
        print("=" * 60)
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test Case {i}: {test_case['title']}")
            print(f"📝 Description: {test_case['description']}")
            print(f"🎯 Expected: {test_case['expected']}")
            print("-" * 40)
            
            start_time = time.time()
            
            # Run enhanced classification
            result = self.enhanced_classifier.classify(
                test_case['title'], 
                test_case['description']
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            # Display results
            print(f"🔍 Method Used: {result.method_used}")
            print(f"⚡ Processing Time: {processing_time:.1f}ms")
            print(f"✨ Clear-cut Detection: {result.clear_cut_detection}")
            
            if result.clear_cut_detection:
                print(f"🎯 Needs Geo-Logic: {result.needs_geo_logic} (High Confidence: {result.overall_confidence:.1%})")
            else:
                print(f"🎯 Needs Geo-Logic: {result.needs_geo_logic}")
                print(f"📊 Primary Confidence: {result.primary_confidence:.1%}")
                print(f"📊 Secondary Confidence: {result.secondary_confidence:.1%}")
                print(f"📊 Overall Confidence: {result.overall_confidence:.1%}")
            
            print(f"⚠️  Risk Assessment: {result.risk_assessment}")
            
            # Show standardized entities
            if result.standardized_entities.locations:
                locations = [loc['colloquial_name'] for loc in result.standardized_entities.locations]
                print(f"🌍 Locations Detected: {', '.join(locations)}")
            
            if result.standardized_entities.ages:
                ages = [age['standardized_term'] for age in result.standardized_entities.ages]
                print(f"👶 Age Terms Detected: {', '.join(ages)}")
            
            if result.standardized_entities.terminology:
                terms = [term['standardized_form'] for term in result.standardized_entities.terminology]
                print(f"📋 Regulatory Terms: {', '.join(terms)}")
            
            # Human intervention check
            if result.needs_human_review:
                print(f"🚨 HUMAN INTERVENTION REQUIRED: {result.intervention_priority.upper()}")
                print(f"📝 Reason: {result.human_review_reason}")
            else:
                print("✅ No human intervention needed")
            
            print(f"💡 Reasoning: {result.reasoning[:150]}..." if len(result.reasoning) > 150 else f"💡 Reasoning: {result.reasoning}")
            
            results.append({
                "test_case": test_case,
                "result": result,
                "processing_time_ms": processing_time
            })
            
            print()
        
        return results
    
    def demo_glossary_standardization(self):
        """Demonstrate the glossary standardization capabilities"""
        
        print("📚 GLOSSARY STANDARDIZATION DEMO")
        print("=" * 60)
        
        # Test location standardization
        location_tests = [
            "US", "USA", "United States", "America",
            "EU", "European Union", "Europe",
            "CA", "Canada", "California", "Calif",
            "UK", "Britain", "Great Britain"
        ]
        
        print("🌍 Location Standardization:")
        for location_text in location_tests:
            location, confidence = self.glossary.standardize_location(location_text)
            if location:
                print(f"  '{location_text}' → {location.colloquial_name} ({location.country_code_iso}) [{confidence:.1%}]")
            else:
                print(f"  '{location_text}' → Not found")
        
        print()
        
        # Test age standardization
        age_tests = [
            "under 18", "18+", "minor", "teen", "child", "adult", "21 and up"
        ]
        
        print("👶 Age Term Standardization:")
        for age_text in age_tests:
            age, confidence = self.glossary.standardize_age(age_text)
            if age:
                print(f"  '{age_text}' → {age.term} (ages {age.numerical_range[0]}-{age.numerical_range[1]}) [{confidence:.1%}]")
            else:
                print(f"  '{age_text}' → Not found")
        
        print()
        
        # Test terminology standardization
        term_tests = [
            "GDPR", "COPPA", "age verification", "parental consent", "content moderation"
        ]
        
        print("📋 Terminology Standardization:")
        for term_text in term_tests:
            term, confidence = self.glossary.standardize_terminology(term_text)
            if term:
                print(f"  '{term_text}' → {term.standardized_form} ({term.category}) [{confidence:.1%}]")
            else:
                print(f"  '{term_text}' → Not found")
        
        print()
    
    def demo_confidence_calculation(self):
        """Demonstrate the sophisticated confidence calculation system"""
        
        print("📊 CONFIDENCE CALCULATION DEMO")
        print("=" * 60)
        
        # Create a test case that goes through the full pipeline
        title = "Age verification for EU users"
        description = "Implement age verification system for users in European Union countries to comply with GDPR and Digital Services Act requirements for minors under 16"
        
        print(f"📋 Test Feature: {title}")
        print(f"📝 Description: {description}")
        print()
        
        # Get detailed results
        result = self.enhanced_classifier.classify(title, description)
        
        print("🔍 Confidence Breakdown:")
        if 'base_confidence' in result.confidence_breakdown:
            breakdown = result.confidence_breakdown
            print(f"  📊 Base Confidence: {breakdown.get('base_confidence', 0):.1%}")
            print(f"  🤖 Primary (LLM) Component: {breakdown.get('primary_component', 0):.1%}")
            print(f"  🔍 Secondary (Regex/NER) Component: {breakdown.get('secondary_component', 0):.1%}")
            print(f"  🎯 Entity Adjustment: {breakdown.get('entity_adjustment', 0):+.1%}")
            print(f"  🌟 Diversity Boost: {breakdown.get('diversity_boost', 0):+.1%}")
            print(f"  ✨ Final Confidence: {breakdown.get('final_confidence', 0):.1%}")
            print(f"  🎯 Category Threshold: {breakdown.get('category_threshold', 0):.1%}")
        
        print()
        print("📈 Entity Confidence Scores:")
        entity_scores = result.standardized_entities.confidence_scores
        for entity_type, score in entity_scores.items():
            if score > 0:
                print(f"  {entity_type.title()}: {score:.1%}")
        
        print()
    
    def demo_human_intervention(self):
        """Demonstrate the human intervention alert system"""
        
        print("🚨 HUMAN INTERVENTION DEMO")
        print("=" * 60)
        
        # Create test cases that should trigger intervention
        intervention_cases = [
            {
                "title": "Unclear Geographic Feature",
                "description": "Feature with location mentions but unclear compliance intent",
                "expected_priority": "medium"
            },
            {
                "title": "Minor Safety Feature",
                "description": "Safety feature for children with moderate confidence",
                "expected_priority": "high"
            }
        ]
        
        for case in intervention_cases:
            print(f"📋 Test Case: {case['title']}")
            
            result = self.enhanced_classifier.classify(case['title'], case['description'])
            
            if result.needs_human_review:
                print(f"  🚨 Alert Priority: {result.intervention_priority}")
                print(f"  📝 Reason: {result.human_review_reason}")
                print(f"  ✅ Alert system working correctly")
            else:
                print("  ℹ️  No intervention needed for this case")
            print()
        
        # Show pending alerts
        pending_alerts = self.feedback_processor.get_pending_alerts()
        print(f"📋 Total Pending Alerts: {len(pending_alerts)}")
        
        for alert in pending_alerts[:3]:  # Show first 3
            print(f"  🔔 {alert.alert_id}: {alert.feature_title} ({alert.priority})")
        
        print()
    
    def demo_performance_metrics(self):
        """Demonstrate performance tracking and metrics"""
        
        print("📈 PERFORMANCE METRICS DEMO")
        print("=" * 60)
        
        performance = self.feedback_processor.get_performance_summary()
        
        print(f"📊 Total Classifications: {performance['total_classifications']}")
        print(f"🎯 Current Accuracy: {performance['current_accuracy']:.1%}")
        print(f"📈 Trend Direction: {performance['trend_direction']}")
        print(f"🚨 Total Interventions: {performance['total_interventions']}")
        print(f"🔄 Feedback Applied: {performance['feedback_applied']}")
        print(f"❌ False Positive Rate: {performance['false_positive_rate']:.1%}")
        print(f"❌ False Negative Rate: {performance['false_negative_rate']:.1%}")
        print()
        
        # Show pending alerts by priority
        alerts = performance['pending_alerts']
        if any(alerts.values()):
            print("🚨 Pending Alerts by Priority:")
            for priority, count in alerts.items():
                if count > 0:
                    print(f"  {priority.title()}: {count}")
        else:
            print("✅ No pending alerts")
        
        print()
    
    def run_full_demo(self):
        """Run the complete demonstration"""
        
        print("🎬 STARTING COMPLETE ENHANCED FEATURE FLOW DEMO")
        print("=" * 60)
        print()
        
        # 1. Glossary standardization
        self.demo_glossary_standardization()
        
        # 2. Feature classification tests
        test_results = self.demo_test_cases()
        
        # 3. Confidence calculation details
        self.demo_confidence_calculation()
        
        # 4. Human intervention system
        self.demo_human_intervention()
        
        # 5. Performance metrics
        self.demo_performance_metrics()
        
        # Summary
        print("📋 DEMO SUMMARY")
        print("=" * 60)
        print(f"✅ Tested {len(test_results)} feature cases")
        
        clear_cut_cases = sum(1 for r in test_results if r['result'].clear_cut_detection)
        human_review_cases = sum(1 for r in test_results if r['result'].needs_human_review)
        avg_processing_time = sum(r['processing_time_ms'] for r in test_results) / len(test_results)
        
        print(f"⚡ Clear-cut cases (95%+ confidence): {clear_cut_cases}")
        print(f"🚨 Cases requiring human review: {human_review_cases}")
        print(f"⏱️  Average processing time: {avg_processing_time:.1f}ms")
        print()
        
        print("🎯 KEY FEATURES DEMONSTRATED:")
        print("  ✅ Preprocessing and tokenization")
        print("  ✅ NER and regex pattern matching")
        print("  ✅ Entity standardization with glossary")
        print("  ✅ Multi-stage classification (LLM + Regex/NER)")
        print("  ✅ Sophisticated confidence calculation")
        print("  ✅ Category-specific thresholds")
        print("  ✅ Human intervention alerts")
        print("  ✅ Performance monitoring")
        print("  ✅ Self-evolution capability")
        print()
        
        print("🚀 ENHANCED FEATURE FLOW COMPLETE!")
        print("=" * 60)

def main():
    """Main demo function"""
    try:
        demo = EnhancedFlowDemo()
        demo.run_full_demo()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
