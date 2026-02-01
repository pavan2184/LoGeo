#!/usr/bin/env python3
"""
Feature Analysis Results - Comprehensive Analysis
Analyzes the results from individual feature classification
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import seaborn as sns

def analyze_feature_results(csv_path):
    """Comprehensive analysis of feature classification results"""
    
    print("📊 COMPREHENSIVE FEATURE ANALYSIS RESULTS")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv(csv_path)
    print(f"📋 Total Features Analyzed: {len(df)}")
    print()
    
    # === GEO-LOGIC REQUIREMENTS ANALYSIS ===
    print("🌍 GEO-LOGIC REQUIREMENTS ANALYSIS")
    print("-" * 50)
    
    geo_logic_counts = df['needs_geo_logic'].value_counts()
    geo_needed = geo_logic_counts.get(True, 0)
    geo_not_needed = geo_logic_counts.get(False, 0)
    
    print(f"✅ Requires Geo-Logic: {geo_needed} features ({geo_needed/len(df)*100:.1f}%)")
    print(f"❌ No Geo-Logic Needed: {geo_not_needed} features ({geo_not_needed/len(df)*100:.1f}%)")
    
    # List features requiring geo-logic
    geo_features = df[df['needs_geo_logic'] == True]['feature_name'].tolist()
    print(f"\n🎯 Features Requiring Geo-Logic:")
    for i, feature in enumerate(geo_features, 1):
        print(f"  {i}. {feature}")
    
    print()
    
    # === CONFIDENCE ANALYSIS ===
    print("📊 CONFIDENCE SCORE ANALYSIS")
    print("-" * 50)
    
    # Overall confidence statistics
    conf_stats = df['overall_confidence'].describe()
    print(f"📈 Confidence Statistics:")
    print(f"  Mean: {conf_stats['mean']:.3f}")
    print(f"  Median: {conf_stats['50%']:.3f}")
    print(f"  Std Dev: {conf_stats['std']:.3f}")
    print(f"  Min: {conf_stats['min']:.3f}")
    print(f"  Max: {conf_stats['max']:.3f}")
    
    # Confidence distribution
    high_conf = len(df[df['overall_confidence'] >= 0.8])
    medium_conf = len(df[(df['overall_confidence'] >= 0.5) & (df['overall_confidence'] < 0.8)])
    low_conf = len(df[df['overall_confidence'] < 0.5])
    
    print(f"\n🎯 Confidence Distribution:")
    print(f"  High (≥80%): {high_conf} features ({high_conf/len(df)*100:.1f}%)")
    print(f"  Medium (50-79%): {medium_conf} features ({medium_conf/len(df)*100:.1f}%)")
    print(f"  Low (<50%): {low_conf} features ({low_conf/len(df)*100:.1f}%)")
    
    print()
    
    # === RISK ASSESSMENT ANALYSIS ===
    print("⚠️  RISK ASSESSMENT ANALYSIS")
    print("-" * 50)
    
    risk_counts = df['risk_assessment'].value_counts()
    print(f"📈 Risk Level Distribution:")
    for risk_level, count in risk_counts.items():
        percentage = count/len(df)*100
        print(f"  {risk_level.title()}: {count} features ({percentage:.1f}%)")
    
    # High-risk features
    high_risk_features = df[df['risk_assessment'].isin(['critical', 'high'])]
    if len(high_risk_features) > 0:
        print(f"\n🚨 High-Risk Features:")
        for _, feature in high_risk_features.iterrows():
            print(f"  • {feature['feature_name']} ({feature['risk_assessment']})")
    
    print()
    
    # === CLEAR-CUT DETECTION ANALYSIS ===
    print("⚡ CLEAR-CUT DETECTION ANALYSIS")
    print("-" * 50)
    
    clear_cut_counts = df['clear_cut_detection'].value_counts()
    clear_cut_yes = clear_cut_counts.get(True, 0)
    clear_cut_no = clear_cut_counts.get(False, 0)
    
    print(f"✨ Clear-cut Cases: {clear_cut_yes} features ({clear_cut_yes/len(df)*100:.1f}%)")
    print(f"🔍 Requires Analysis: {clear_cut_no} features ({clear_cut_no/len(df)*100:.1f}%)")
    
    # List clear-cut features
    clear_cut_features = df[df['clear_cut_detection'] == True]['feature_name'].tolist()
    if clear_cut_features:
        print(f"\n⚡ Clear-cut Features:")
        for i, feature in enumerate(clear_cut_features, 1):
            print(f"  {i}. {feature}")
    
    print()
    
    # === HUMAN REVIEW ANALYSIS ===
    print("🚨 HUMAN INTERVENTION ANALYSIS")
    print("-" * 50)
    
    review_counts = df['needs_human_review'].value_counts()
    review_needed = review_counts.get(True, 0)
    review_not_needed = review_counts.get(False, 0)
    
    print(f"🚨 Needs Human Review: {review_needed} features ({review_needed/len(df)*100:.1f}%)")
    print(f"✅ No Review Needed: {review_not_needed} features ({review_not_needed/len(df)*100:.1f}%)")
    
    # Intervention priority breakdown
    priority_counts = df[df['needs_human_review'] == True]['intervention_priority'].value_counts()
    if len(priority_counts) > 0:
        print(f"\n📋 Intervention Priority Breakdown:")
        for priority, count in priority_counts.items():
            print(f"  {priority.title()}: {count} features")
    
    # List features needing review
    review_features = df[df['needs_human_review'] == True][['feature_name', 'human_review_reason', 'intervention_priority']]
    if len(review_features) > 0:
        print(f"\n🔍 Features Requiring Human Review:")
        for _, feature in review_features.iterrows():
            print(f"  • {feature['feature_name']} ({feature['intervention_priority']})")
            print(f"    Reason: {feature['human_review_reason']}")
    
    print()
    
    # === REGULATORY ANALYSIS ===
    print("📋 REGULATORY COMPLIANCE ANALYSIS")
    print("-" * 50)
    
    # Extract regulations
    all_regulations = []
    for reg_str in df['applicable_regulations']:
        if pd.notna(reg_str) and reg_str != '[]':
            try:
                regs = json.loads(reg_str)
                if isinstance(regs, list):
                    for reg in regs:
                        if isinstance(reg, dict) and 'name' in reg:
                            all_regulations.append(reg['name'])
            except:
                continue
    
    if all_regulations:
        reg_counts = Counter(all_regulations)
        print(f"📜 Identified Regulations:")
        for regulation, count in reg_counts.most_common():
            print(f"  • {regulation}: {count} feature(s)")
    else:
        print("📜 No specific regulations identified in current analysis")
    
    print()
    
    # === LOCATION AND AGE ANALYSIS ===
    print("🌍 GEOGRAPHIC AND AGE ANALYSIS")
    print("-" * 50)
    
    # Extract locations
    all_locations = []
    for loc_str in df['detected_locations']:
        if pd.notna(loc_str) and loc_str:
            locations = [loc.strip() for loc in loc_str.split(',') if loc.strip()]
            all_locations.extend(locations)
    
    if all_locations:
        loc_counts = Counter(all_locations)
        print(f"🗺️  Geographic Mentions:")
        for location, count in loc_counts.most_common():
            print(f"  • {location}: {count} feature(s)")
    
    # Extract age terms
    all_ages = []
    for age_str in df['detected_ages']:
        if pd.notna(age_str) and age_str:
            ages = [age.strip() for age in age_str.split(',') if age.strip()]
            all_ages.extend(ages)
    
    if all_ages:
        age_counts = Counter(all_ages)
        print(f"\n👶 Age-Related Terms:")
        for age_term, count in age_counts.most_common():
            print(f"  • {age_term}: {count} feature(s)")
    
    print()
    
    # === PERFORMANCE ANALYSIS ===
    print("⏱️  PROCESSING PERFORMANCE ANALYSIS")
    print("-" * 50)
    
    processing_stats = df['processing_time_ms'].describe()
    print(f"⚡ Processing Time Statistics (milliseconds):")
    print(f"  Mean: {processing_stats['mean']:.2f}ms")
    print(f"  Median: {processing_stats['50%']:.2f}ms")
    print(f"  Min: {processing_stats['min']:.2f}ms")
    print(f"  Max: {processing_stats['max']:.2f}ms")
    print(f"  Total Time: {df['processing_time_ms'].sum():.2f}ms")
    
    print()
    
    # === PATTERN MATCHING ANALYSIS ===
    print("🔍 PATTERN MATCHING ANALYSIS")
    print("-" * 50)
    
    # Parse pattern matches
    total_high_matches = 0
    total_medium_matches = 0
    total_location_matches = 0
    total_age_matches = 0
    
    for pattern_str in df['pattern_matches']:
        if pd.notna(pattern_str):
            try:
                patterns = json.loads(pattern_str)
                total_high_matches += patterns.get('high_confidence', 0)
                total_medium_matches += patterns.get('medium_confidence', 0)
                total_location_matches += patterns.get('location_indicators', 0)
                total_age_matches += patterns.get('age_indicators', 0)
            except:
                continue
    
    print(f"📊 Pattern Match Summary:")
    print(f"  High Confidence Patterns: {total_high_matches} matches")
    print(f"  Medium Confidence Patterns: {total_medium_matches} matches")
    print(f"  Location Indicators: {total_location_matches} matches")
    print(f"  Age Indicators: {total_age_matches} matches")
    
    print()
    
    # === RECOMMENDATIONS SUMMARY ===
    print("💡 RECOMMENDATIONS SUMMARY")
    print("-" * 50)
    
    geo_logic_features = df[df['needs_geo_logic'] == True]
    high_risk_count = len(df[df['risk_assessment'].isin(['critical', 'high'])])
    review_needed_count = len(df[df['needs_human_review'] == True])
    
    print(f"🎯 Priority Actions Needed:")
    print(f"  1. Implement geo-logic for {len(geo_logic_features)} features")
    print(f"  2. Prioritize legal review for {high_risk_count} high-risk features")
    print(f"  3. Schedule human review for {review_needed_count} uncertain cases")
    
    # Features needing immediate attention
    immediate_attention = df[
        (df['risk_assessment'].isin(['critical', 'high'])) | 
        (df['needs_human_review'] == True) |
        (df['needs_geo_logic'] == True)
    ]['feature_name'].unique()
    
    print(f"\n🚨 Features Requiring Immediate Attention ({len(immediate_attention)}):")
    for i, feature in enumerate(immediate_attention, 1):
        feature_data = df[df['feature_name'] == feature].iloc[0]
        flags = []
        if feature_data['needs_geo_logic']:
            flags.append("Geo-Logic")
        if feature_data['risk_assessment'] in ['critical', 'high']:
            flags.append(f"{feature_data['risk_assessment'].title()} Risk")
        if feature_data['needs_human_review']:
            flags.append("Human Review")
        
        print(f"  {i}. {feature}")
        print(f"     Flags: {', '.join(flags)}")
    
    print()
    print("✅ Analysis Complete!")
    print("=" * 70)
    
    return df

def main():
    """Main analysis function"""
    try:
        df = analyze_feature_results('feature_analysis_results.csv')
        
        # Save summary statistics
        summary_stats = {
            'total_features': len(df),
            'geo_logic_needed': len(df[df['needs_geo_logic'] == True]),
            'high_risk_features': len(df[df['risk_assessment'].isin(['critical', 'high'])]),
            'clear_cut_cases': len(df[df['clear_cut_detection'] == True]),
            'human_review_needed': len(df[df['needs_human_review'] == True]),
            'avg_confidence': df['overall_confidence'].mean(),
            'avg_processing_time': df['processing_time_ms'].mean()
        }
        
        with open('analysis_summary.json', 'w') as f:
            json.dump(summary_stats, f, indent=2)
        
        print(f"\n📊 Summary statistics saved to: analysis_summary.json")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
