#!/usr/bin/env python3
"""
Analysis of why applicable regulations are mostly empty
"""

import pandas as pd
import json
import re

def analyze_regulation_detection():
    """Analyze why regulation detection is failing"""
    
    print("🔍 REGULATION DETECTION ANALYSIS")
    print("=" * 60)
    
    # Load the results
    df = pd.read_csv('feature_analysis_results.csv')
    
    # Current regulation dictionary from the simple analyzer
    regulations = {
        'GDPR': 'EU General Data Protection Regulation',
        'COPPA': 'US Children\'s Online Privacy Protection Act',
        'CCPA': 'California Consumer Privacy Act',
        'DSA': 'EU Digital Services Act',
        'Utah Social Media Regulation Act': 'Utah minor protection legislation',
        'SB976': 'California Age-Appropriate Design Code Act',
        'Florida Online Protections for Minors': 'Florida minor protection law'
    }
    
    print("📋 CURRENT REGULATION DETECTION LOGIC:")
    print("Looking for exact matches of regulation names in feature text")
    print()
    
    print("🎯 IDENTIFIED ISSUES:")
    print("1. Too restrictive - looks for exact regulation names")
    print("2. Misses implied regulatory connections")
    print("3. Doesn't catch regulatory concepts without explicit names")
    print()
    
    # Analyze each feature to show what regulations SHOULD be detected
    print("📊 FEATURE-BY-FEATURE ANALYSIS:")
    print("-" * 50)
    
    for i, row in df.iterrows():
        feature_name = row['feature_name']
        description = row['feature_description']
        current_regs = row['applicable_regulations']
        
        full_text = f"{feature_name} {description}".lower()
        
        print(f"\n{i+1}. {feature_name}")
        print(f"   Current regulations: {current_regs}")
        
        # Check what SHOULD be detected based on context
        should_detect = []
        
        # GDPR - EU + minors/privacy
        if re.search(r'\b(eu|european union|europe)\b', full_text, re.IGNORECASE):
            if re.search(r'\b(minor|child|under \d+|privacy|data protection)\b', full_text, re.IGNORECASE):
                should_detect.append("GDPR (EU + minors/privacy context)")
        
        # COPPA - US + children under 13
        if re.search(r'\b(us|usa|united states|america|federal)\b', full_text, re.IGNORECASE):
            if re.search(r'\b(child|under 13|ncmec|child abuse)\b', full_text, re.IGNORECASE):
                should_detect.append("COPPA (US + children context)")
        
        # California laws
        if re.search(r'\b(california|ca)\b', full_text, re.IGNORECASE):
            if re.search(r'\b(teen|minor|under 18|privacy|personalization)\b', full_text, re.IGNORECASE):
                should_detect.append("CCPA/SB976 (California + minors)")
        
        # Utah law
        if re.search(r'\butah\b', full_text, re.IGNORECASE):
            if re.search(r'\b(minor|under 18|curfew|social media)\b', full_text, re.IGNORECASE):
                should_detect.append("Utah Social Media Regulation Act")
        
        # Florida law
        if re.search(r'\bflorida\b', full_text, re.IGNORECASE):
            if re.search(r'\b(minor|child|protection|parental)\b', full_text, re.IGNORECASE):
                should_detect.append("Florida Online Protections for Minors")
        
        # DSA - EU + content/transparency
        if re.search(r'\b(eu|european)\b', full_text, re.IGNORECASE):
            if re.search(r'\b(content|transparency|dsa|digital services)\b', full_text, re.IGNORECASE):
                should_detect.append("DSA (EU Digital Services Act)")
        
        # NCMEC reporting requirements
        if re.search(r'\b(ncmec|child abuse|sexual abuse|child sexual)\b', full_text, re.IGNORECASE):
            should_detect.append("US Federal Law (NCMEC reporting)")
        
        if should_detect:
            print(f"   Should detect: {', '.join(should_detect)}")
        else:
            print(f"   Should detect: None (correctly detected)")
    
    print("\n" + "="*60)
    print("🔧 RECOMMENDED FIXES:")
    print("1. Use contextual detection instead of exact string matching")
    print("2. Look for regulation concepts (jurisdiction + subject matter)")
    print("3. Add pattern-based detection for regulatory indicators")
    print("4. Consider implicit regulatory requirements")
    
    # Show statistics
    total_features = len(df)
    current_with_regs = len(df[df['applicable_regulations'] != '[]'])
    
    print(f"\n📊 CURRENT STATISTICS:")
    print(f"Total features: {total_features}")
    print(f"Features with detected regulations: {current_with_regs}")
    print(f"Features missing regulations: {total_features - current_with_regs}")
    print(f"Detection rate: {current_with_regs/total_features*100:.1f}%")

def create_improved_regulation_detector():
    """Create an improved regulation detection function"""
    
    print("\n🚀 IMPROVED REGULATION DETECTION LOGIC")
    print("=" * 60)
    
    df = pd.read_csv('feature_analysis_results.csv')
    
    def detect_regulations_improved(title: str, description: str):
        """Improved regulation detection using contextual analysis"""
        full_text = f"{title} {description}".lower()
        detected_regulations = []
        
        # GDPR Detection
        if re.search(r'\b(eu|european union|europe)\b', full_text, re.IGNORECASE):
            if re.search(r'\b(minor|child|under 16|privacy|data protection|consent)\b', full_text, re.IGNORECASE):
                detected_regulations.append({
                    "name": "GDPR",
                    "full_name": "EU General Data Protection Regulation",
                    "jurisdiction": "EU",
                    "relevance": "high",
                    "reason": "EU jurisdiction with minor/privacy context"
                })
        
        # COPPA Detection
        if re.search(r'\b(us|usa|united states|america|federal)\b', full_text, re.IGNORECASE):
            if re.search(r'\b(child|under 13|ncmec|child abuse|child sexual)\b', full_text, re.IGNORECASE):
                detected_regulations.append({
                    "name": "COPPA",
                    "full_name": "US Children's Online Privacy Protection Act",
                    "jurisdiction": "US",
                    "relevance": "high",
                    "reason": "US jurisdiction with children under 13 context"
                })
        
        # California Laws
        if re.search(r'\b(california|ca)\b', full_text, re.IGNORECASE) and re.search(r'\bsb976\b', full_text, re.IGNORECASE):
            detected_regulations.append({
                "name": "SB976",
                "full_name": "California Age-Appropriate Design Code Act",
                "jurisdiction": "California",
                "relevance": "high",
                "reason": "Explicit SB976 mention"
            })
        elif re.search(r'\b(california|ca)\b', full_text, re.IGNORECASE):
            if re.search(r'\b(teen|minor|under 18|privacy|personalization)\b', full_text, re.IGNORECASE):
                detected_regulations.append({
                    "name": "CCPA/SB976",
                    "full_name": "California Consumer Privacy Act / Age-Appropriate Design Code",
                    "jurisdiction": "California",
                    "relevance": "medium",
                    "reason": "California jurisdiction with minor privacy context"
                })
        
        # Utah Law
        if re.search(r'\butah\b', full_text, re.IGNORECASE):
            if re.search(r'\b(minor|under 18|curfew|social media|regulation act)\b', full_text, re.IGNORECASE):
                detected_regulations.append({
                    "name": "Utah Social Media Regulation Act",
                    "full_name": "Utah minor protection legislation",
                    "jurisdiction": "Utah",
                    "relevance": "high",
                    "reason": "Utah jurisdiction with social media minor context"
                })
        
        # Florida Law
        if re.search(r'\bflorida\b', full_text, re.IGNORECASE):
            if re.search(r'\b(minor|child|protection|parental|online protections)\b', full_text, re.IGNORECASE):
                detected_regulations.append({
                    "name": "Florida Online Protections for Minors",
                    "full_name": "Florida minor protection law",
                    "jurisdiction": "Florida",
                    "relevance": "high",
                    "reason": "Florida jurisdiction with minor protection context"
                })
        
        # EU DSA
        if re.search(r'\b(eu|european)\b', full_text, re.IGNORECASE):
            if re.search(r'\b(dsa|digital services act|content|transparency|flagged|removal)\b', full_text, re.IGNORECASE):
                detected_regulations.append({
                    "name": "DSA",
                    "full_name": "EU Digital Services Act",
                    "jurisdiction": "EU",
                    "relevance": "high",
                    "reason": "EU jurisdiction with content transparency context"
                })
        
        # NCMEC Reporting (US Federal)
        if re.search(r'\b(ncmec|child abuse|sexual abuse|child sexual|federal law|report.*child)\b', full_text, re.IGNORECASE):
            detected_regulations.append({
                "name": "US Federal NCMEC Reporting",
                "full_name": "US Federal law requiring NCMEC reporting",
                "jurisdiction": "US",
                "relevance": "critical",
                "reason": "Child abuse content reporting requirements"
            })
        
        return detected_regulations
    
    # Test improved detection
    improved_results = []
    for _, row in df.iterrows():
        improved_regs = detect_regulations_improved(row['feature_name'], row['feature_description'])
        improved_results.append({
            'feature_name': row['feature_name'],
            'original_regs': row['applicable_regulations'],
            'improved_regs': improved_regs,
            'improvement': len(improved_regs) > (0 if row['applicable_regulations'] == '[]' else len(json.loads(row['applicable_regulations'])))
        })
    
    print("📊 IMPROVED DETECTION RESULTS:")
    print("-" * 40)
    
    improvements = 0
    for result in improved_results:
        if result['improvement']:
            improvements += 1
            print(f"\n✅ {result['feature_name']}")
            print(f"   Original: {result['original_regs']}")
            print(f"   Improved: {len(result['improved_regs'])} regulation(s) detected")
            for reg in result['improved_regs']:
                print(f"     • {reg['name']} ({reg['reason']})")
    
    total_with_improved = sum(1 for r in improved_results if len(r['improved_regs']) > 0)
    
    print(f"\n📈 IMPROVEMENT STATISTICS:")
    print(f"Features with improved detection: {improvements}")
    print(f"Total features with regulations (improved): {total_with_improved}")
    print(f"Improved detection rate: {total_with_improved/len(df)*100:.1f}%")

if __name__ == "__main__":
    analyze_regulation_detection()
    create_improved_regulation_detector()
