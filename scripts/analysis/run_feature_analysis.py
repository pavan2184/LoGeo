#!/usr/bin/env python3
"""
Individual Feature Analysis Script
Processes each feature through the enhanced classification system and saves results to CSV
"""

import pandas as pd
import json
import csv
import os
import sys
import time
from datetime import datetime
from dataclasses import asdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.enhanced_classifier import get_enhanced_classifier
from backend.feedback_system import get_feedback_processor, FeedbackType, InterventionPriority

def process_features_individually(input_csv_path, output_csv_path):
    """
    Process each feature individually through the enhanced classification system
    """
    print("🚀 Starting Individual Feature Analysis")
    print("=" * 60)
    
    # Initialize the enhanced classifier
    print("📦 Initializing enhanced classifier...")
    enhanced_classifier = get_enhanced_classifier()
    feedback_processor = get_feedback_processor()
    
    # Read input features
    print(f"📖 Reading features from: {input_csv_path}")
    df = pd.read_csv(input_csv_path)
    
    print(f"✅ Found {len(df)} features to analyze")
    print()
    
    results = []
    
    for i, row in df.iterrows():
        feature_name = str(row['feature_name']) if pd.notna(row['feature_name']) else ""
        feature_description = str(row['feature_description']) if pd.notna(row['feature_description']) else ""
        
        print(f"🔍 Analyzing Feature {i+1}/{len(df)}: {feature_name[:50]}...")
        
        start_time = time.time()
        
        try:
            # Run enhanced classification
            result = enhanced_classifier.classify(feature_name, feature_description)
            processing_time = (time.time() - start_time) * 1000
            
            # Create intervention alert if needed
            if result.needs_human_review:
                priority_map = {
                    "low": InterventionPriority.LOW,
                    "medium": InterventionPriority.MEDIUM, 
                    "high": InterventionPriority.HIGH,
                    "critical": InterventionPriority.CRITICAL
                }
                
                alert_id = feedback_processor.create_intervention_alert(
                    feature_name,
                    feature_description,
                    asdict(result),
                    result.human_review_reason,
                    priority_map.get(result.intervention_priority, InterventionPriority.MEDIUM)
                )
                
                print(f"  🚨 Human intervention alert created: {alert_id}")
            
            # Prepare result row
            result_row = {
                'timestamp': datetime.now().isoformat(),
                'feature_name': feature_name,
                'feature_description': feature_description,
                'needs_geo_logic': result.needs_geo_logic,
                'primary_confidence': result.primary_confidence,
                'secondary_confidence': result.secondary_confidence,
                'overall_confidence': result.overall_confidence,
                'reasoning': result.reasoning,
                'applicable_regulations': json.dumps(result.applicable_regulations),
                'risk_assessment': result.risk_assessment,
                'regulatory_requirements': "; ".join(result.regulatory_requirements),
                'evidence_sources': "; ".join(result.evidence_sources),
                'recommended_actions': "; ".join(result.recommended_actions),
                'standardized_entities': json.dumps(asdict(result.standardized_entities)),
                'clear_cut_detection': result.clear_cut_detection,
                'confidence_breakdown': json.dumps(result.confidence_breakdown),
                'needs_human_review': result.needs_human_review,
                'human_review_reason': result.human_review_reason,
                'intervention_priority': result.intervention_priority,
                'method_used': result.method_used,
                'processing_time_ms': processing_time
            }
            
            results.append(result_row)
            
            # Show brief status
            status = "✅ Clear-cut" if result.clear_cut_detection else f"🔍 {result.overall_confidence:.1%} confidence"
            geo_status = "🌍 Geo-logic needed" if result.needs_geo_logic else "🏠 No geo-logic"
            review_status = f" | 🚨 Review: {result.intervention_priority}" if result.needs_human_review else ""
            
            print(f"  {status} | {geo_status}{review_status}")
            
        except Exception as e:
            print(f"  ❌ Error processing feature: {e}")
            # Add error row
            result_row = {
                'timestamp': datetime.now().isoformat(),
                'feature_name': feature_name,
                'feature_description': feature_description,
                'needs_geo_logic': None,
                'primary_confidence': None,
                'secondary_confidence': None,
                'overall_confidence': None,
                'reasoning': f"Error: {str(e)}",
                'applicable_regulations': "[]",
                'risk_assessment': "error",
                'regulatory_requirements': "",
                'evidence_sources': "",
                'recommended_actions': "",
                'standardized_entities': "{}",
                'clear_cut_detection': False,
                'confidence_breakdown': "{}",
                'needs_human_review': True,
                'human_review_reason': f"Processing error: {str(e)}",
                'intervention_priority': "high",
                'method_used': "error",
                'processing_time_ms': (time.time() - start_time) * 1000
            }
            results.append(result_row)
    
    # Save results to CSV
    print(f"\n💾 Saving results to: {output_csv_path}")
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv_path, index=False)
    
    print("=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    
    # Calculate summary statistics
    total_features = len(results)
    successful_analyses = len([r for r in results if r['needs_geo_logic'] is not None])
    geo_logic_needed = len([r for r in results if r['needs_geo_logic'] == True])
    clear_cut_cases = len([r for r in results if r['clear_cut_detection'] == True])
    human_review_cases = len([r for r in results if r['needs_human_review'] == True])
    avg_processing_time = sum([r['processing_time_ms'] for r in results]) / len(results)
    
    print(f"📋 Total Features Analyzed: {total_features}")
    print(f"✅ Successful Analyses: {successful_analyses}")
    print(f"🌍 Geo-logic Required: {geo_logic_needed}")
    print(f"⚡ Clear-cut Detections: {clear_cut_cases}")
    print(f"🚨 Human Review Required: {human_review_cases}")
    print(f"⏱️  Average Processing Time: {avg_processing_time:.1f}ms")
    
    # Risk assessment breakdown
    risk_counts = {}
    for result in results:
        risk = result.get('risk_assessment', 'unknown')
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    print(f"\n📈 Risk Assessment Breakdown:")
    for risk_level, count in sorted(risk_counts.items()):
        print(f"  {risk_level.title()}: {count}")
    
    print(f"\n✅ Results saved to: {output_csv_path}")
    print("🚀 Individual Feature Analysis Complete!")
    
    return output_df

def main():
    """Main function"""
    input_file = "input_features.csv"
    output_file = "feature_analysis_results.csv"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    try:
        result_df = process_features_individually(input_file, output_file)
        print(f"\n📄 Results file created with {len(result_df)} rows")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
