#!/usr/bin/env python3
"""
Reorder CSV columns to put feature name/description first, then confidence breakdowns
"""

import pandas as pd

def reorder_csv_with_feature_first():
    """Reorder columns: feature info first, then confidence breakdowns, then everything else"""
    
    print("🔄 REORDERING CSV - FEATURE INFO FIRST")
    print("=" * 60)
    
    # Read the current CSV
    df = pd.read_csv('feature_analysis_results.csv')
    
    print(f"📖 Original columns: {len(df.columns)}")
    
    # Define the new column order
    feature_info_columns = [
        'feature_name',
        'feature_description'
    ]
    
    confidence_columns = [
        'entity_detection_confidence',
        'entity_confidence_level', 
        'classification_confidence',
        'classification_level',
        'law_matching_confidence',
        'law_matching_level'
    ]
    
    # Get all other columns (excluding feature info and confidence columns)
    exclude_columns = feature_info_columns + confidence_columns
    other_columns = [col for col in df.columns if col not in exclude_columns]
    
    # Create new column order: feature info first, then confidence, then everything else
    new_column_order = feature_info_columns + confidence_columns + other_columns
    
    # Reorder the DataFrame
    df_reordered = df[new_column_order]
    
    # Save the reordered CSV
    df_reordered.to_csv('feature_analysis_results.csv', index=False)
    
    print(f"✅ Reordered columns: {len(df_reordered.columns)}")
    print(f"📊 New column order:")
    print(f"   Columns 1-2: Feature identification")
    for i, col in enumerate(feature_info_columns, 1):
        print(f"     {i}. {col}")
    
    print(f"   Columns 3-8: Confidence breakdowns")
    for i, col in enumerate(confidence_columns, 3):
        print(f"     {i}. {col}")
    
    print(f"   Columns 9+: Other analysis data")
    
    print(f"\n💾 Updated file: feature_analysis_results.csv")
    
    return df_reordered

if __name__ == "__main__":
    reordered_df = reorder_csv_with_feature_first()
    
    # Show sample of reordered data
    print(f"\n📋 SAMPLE OF REORDERED DATA:")
    print("-" * 50)
    
    sample = reordered_df[['feature_name', 'feature_description',
                          'entity_detection_confidence', 'entity_confidence_level',
                          'classification_confidence', 'classification_level', 
                          'law_matching_confidence', 'law_matching_level']].head(3)
    
    for i, row in sample.iterrows():
        name = row['feature_name'][:45] + "..." if len(row['feature_name']) > 45 else row['feature_name']
        desc = row['feature_description'][:60] + "..." if len(row['feature_description']) > 60 else row['feature_description']
        
        print(f"\n🎯 Feature: {name}")
        print(f"   Description: {desc}")
        print(f"   Entity: {row['entity_detection_confidence']:.1%} ({row['entity_confidence_level']})")
        print(f"   Classification: {row['classification_confidence']:.1%} ({row['classification_level']})")
        print(f"   Law Matching: {row['law_matching_confidence']:.1%} ({row['law_matching_level']})")
