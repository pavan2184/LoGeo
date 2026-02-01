#!/usr/bin/env python3
"""
Reorder CSV columns to put confidence breakdowns at the front
"""

import pandas as pd

def reorder_csv_columns():
    """Reorder columns to put confidence breakdowns first"""
    
    print("🔄 REORDERING CSV COLUMNS")
    print("=" * 50)
    
    # Read the current CSV
    df = pd.read_csv('feature_analysis_results.csv')
    
    print(f"📖 Original columns: {len(df.columns)}")
    
    # Define the confidence columns that should be first
    confidence_columns = [
        'entity_detection_confidence',
        'entity_confidence_level', 
        'classification_confidence',
        'classification_level',
        'law_matching_confidence',
        'law_matching_level'
    ]
    
    # Get all other columns (excluding the confidence columns)
    other_columns = [col for col in df.columns if col not in confidence_columns]
    
    # Create new column order: confidence columns first, then everything else
    new_column_order = confidence_columns + other_columns
    
    # Reorder the DataFrame
    df_reordered = df[new_column_order]
    
    # Save the reordered CSV
    df_reordered.to_csv('feature_analysis_results.csv', index=False)
    
    print(f"✅ Reordered columns: {len(df_reordered.columns)}")
    print(f"📊 First 6 columns are now confidence breakdowns:")
    for i, col in enumerate(confidence_columns, 1):
        print(f"   {i}. {col}")
    
    print(f"\n💾 Updated file: feature_analysis_results.csv")
    
    return df_reordered

if __name__ == "__main__":
    reordered_df = reorder_csv_columns()
    
    # Show sample of reordered data
    print(f"\n📋 SAMPLE OF REORDERED DATA:")
    print("-" * 40)
    
    sample = reordered_df[['entity_detection_confidence', 'entity_confidence_level',
                          'classification_confidence', 'classification_level', 
                          'law_matching_confidence', 'law_matching_level',
                          'feature_name']].head(3)
    
    for i, row in sample.iterrows():
        name = row['feature_name'][:40] + "..." if len(row['feature_name']) > 40 else row['feature_name']
        print(f"\n🎯 {name}")
        print(f"   Entity: {row['entity_detection_confidence']:.1%} ({row['entity_confidence_level']})")
        print(f"   Classification: {row['classification_confidence']:.1%} ({row['classification_level']})")
        print(f"   Law Matching: {row['law_matching_confidence']:.1%} ({row['law_matching_level']})")
