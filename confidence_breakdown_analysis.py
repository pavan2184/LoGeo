#!/usr/bin/env python3
"""
Detailed Confidence Breakdown Analysis
Shows Entity Detection, Classification, and Law Matching confidence levels
"""

import pandas as pd
import numpy as np

def analyze_confidence_breakdowns():
    """Analyze detailed confidence breakdowns across all components"""
    
    print("🔍 DETAILED CONFIDENCE BREAKDOWN ANALYSIS")
    print("=" * 70)
    
    df = pd.read_csv('feature_analysis_results.csv')
    
    # Calculate average confidence for each component
    entity_avg = df['entity_detection_confidence'].mean()
    classification_avg = df['classification_confidence'].mean()
    law_matching_avg = df['law_matching_confidence'].mean()
    
    print("📊 OVERALL CONFIDENCE AVERAGES:")
    print("-" * 50)
    
    # Format as requested by user
    entity_icon = "⚠️" if entity_avg < 0.7 else "✅" if entity_avg >= 0.8 else "🔍"
    entity_level = "Low" if entity_avg < 0.5 else "Medium" if entity_avg < 0.8 else "High"
    
    classification_icon = "⚠️" if classification_avg < 0.7 else "✅" if classification_avg >= 0.8 else "🔍"
    classification_level = "Low" if classification_avg < 0.5 else "Medium" if classification_avg < 0.8 else "High"
    
    law_icon = "❌" if law_matching_avg < 0.5 else "⚠️" if law_matching_avg < 0.7 else "✅"
    law_level = "Low" if law_matching_avg < 0.5 else "Medium" if law_matching_avg < 0.8 else "High"
    
    print(f"Entity Detection {entity_icon} ({entity_avg*100:.0f}%) - {entity_level} Confidence")
    print(f"Classification {classification_icon} ({classification_avg*100:.0f}%) - {classification_level} Confidence")
    print(f"Law Matching {law_icon} ({law_matching_avg*100:.0f}%) - {law_level} Confidence")
    
    print(f"\n📈 CONFIDENCE LEVEL DISTRIBUTIONS:")
    print("-" * 50)
    
    # Entity Detection breakdown
    entity_levels = df['entity_confidence_level'].value_counts()
    print(f"🔍 Entity Detection:")
    for level, count in entity_levels.items():
        percentage = (count / len(df)) * 100
        print(f"   {level}: {count} features ({percentage:.1f}%)")
    
    # Classification breakdown
    classification_levels = df['classification_level'].value_counts()
    print(f"\n🎯 Classification:")
    for level, count in classification_levels.items():
        percentage = (count / len(df)) * 100
        print(f"   {level}: {count} features ({percentage:.1f}%)")
    
    # Law Matching breakdown
    law_levels = df['law_matching_level'].value_counts()
    print(f"\n⚖️  Law Matching:")
    for level, count in law_levels.items():
        percentage = (count / len(df)) * 100
        print(f"   {level}: {count} features ({percentage:.1f}%)")
    
    print(f"\n🎯 FEATURE EXAMPLES BY CONFIDENCE LEVEL:")
    print("-" * 50)
    
    # Show examples for each component
    print(f"\n📊 Entity Detection Examples:")
    high_entity = df[df['entity_confidence_level'] == 'High']['feature_name'].head(3).tolist()
    medium_entity = df[df['entity_confidence_level'] == 'Medium']['feature_name'].head(3).tolist()
    low_entity = df[df['entity_confidence_level'] == 'Low']['feature_name'].head(3).tolist()
    
    if high_entity:
        print(f"   ✅ High: {', '.join([f[:40] + '...' if len(f) > 40 else f for f in high_entity])}")
    if medium_entity:
        print(f"   ⚠️  Medium: {', '.join([f[:40] + '...' if len(f) > 40 else f for f in medium_entity])}")
    if low_entity:
        print(f"   ❌ Low: {', '.join([f[:40] + '...' if len(f) > 40 else f for f in low_entity])}")
    
    print(f"\n🎯 Classification Examples:")
    high_class = df[df['classification_level'] == 'High']['feature_name'].head(3).tolist()
    medium_class = df[df['classification_level'] == 'Medium']['feature_name'].head(3).tolist()
    low_class = df[df['classification_level'] == 'Low']['feature_name'].head(3).tolist()
    
    if high_class:
        print(f"   ✅ High: {', '.join([f[:40] + '...' if len(f) > 40 else f for f in high_class])}")
    if medium_class:
        print(f"   ⚠️  Medium: {', '.join([f[:40] + '...' if len(f) > 40 else f for f in medium_class])}")
    if low_class:
        print(f"   ❌ Low: {', '.join([f[:40] + '...' if len(f) > 40 else f for f in low_class])}")
    
    print(f"\n⚖️  Law Matching Examples:")
    high_law = df[df['law_matching_level'] == 'High']['feature_name'].head(3).tolist()
    medium_law = df[df['law_matching_level'] == 'Medium']['feature_name'].head(3).tolist()
    low_law = df[df['law_matching_level'] == 'Low']['feature_name'].head(3).tolist()
    
    if high_law:
        print(f"   ✅ High: {', '.join([f[:40] + '...' if len(f) > 40 else f for f in high_law])}")
    if medium_law:
        print(f"   ⚠️  Medium: {', '.join([f[:40] + '...' if len(f) > 40 else f for f in medium_law])}")
    if low_law:
        print(f"   ❌ Low: {', '.join([f[:40] + '...' if len(f) > 40 else f for f in low_law])}")
    
    print(f"\n📋 DETAILED BREAKDOWN FOR SAMPLE FEATURES:")
    print("-" * 50)
    
    # Show detailed breakdown for first 5 features
    sample_features = df.head(5)
    
    for i, row in sample_features.iterrows():
        feature_name = row['feature_name'][:50] + "..." if len(row['feature_name']) > 50 else row['feature_name']
        
        print(f"\n🎯 {feature_name}")
        print(f"   Entity Detection: {row['entity_detection_confidence']:.1%} ({row['entity_confidence_level']})")
        print(f"   Classification: {row['classification_confidence']:.1%} ({row['classification_level']})")
        print(f"   Law Matching: {row['law_matching_confidence']:.1%} ({row['law_matching_level']})")
    
    print(f"\n📄 CSV COLUMNS ADDED:")
    print("-" * 30)
    print(f"   • entity_detection_confidence")
    print(f"   • entity_confidence_level")
    print(f"   • classification_confidence") 
    print(f"   • classification_level")
    print(f"   • law_matching_confidence")
    print(f"   • law_matching_level")
    
    print(f"\n✅ All confidence breakdowns are now included in feature_analysis_results.csv")

if __name__ == "__main__":
    analyze_confidence_breakdowns()
