#!/usr/bin/env python3
"""
Simple Feature Analysis Script
Processes features using rule-based analysis when complex backend isn't available
"""

import pandas as pd
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any

class SimpleFeatureAnalyzer:
    """Simple rule-based feature analyzer"""
    
    def __init__(self):
        # Define patterns for compliance detection
        self.compliance_patterns = {
            'high_confidence': [
                r'\b(comply|compliance)\b.*\b(law|act|regulation|rule)\b',
                r'\b(GDPR|COPPA|CCPA|DSA|Digital Services Act)\b',
                r'\b(Utah|California|EU|European Union|Florida)\b.*\b(minor|child|under \d+)\b',
                r'\b(age verification|parental consent|child protection)\b',
                r'\breport.*\b(NCMEC|law enforcement)\b'
            ],
            'medium_confidence': [
                r'\b(geo|location|region|country)\b.*\b(restrict|limit|block)\b',
                r'\b(minor|child|teen|under \d+)\b.*\b(safety|protection)\b',
                r'\b(privacy|data protection)\b.*\b(minor|child)\b',
                r'\b(jurisdiction|territory|regional)\b'
            ],
            'location_indicators': [
                r'\b(US|USA|United States|America)\b',
                r'\b(EU|European Union|Europe)\b',
                r'\b(CA|Canada|California)\b',
                r'\b(UK|United Kingdom|Britain)\b',
                r'\b(Utah|Florida|Texas)\b'
            ],
            'age_indicators': [
                r'\bunder \d+\b',
                r'\bminor|child|teen|teenager\b',
                r'\b\d+ and (up|under)\b',
                r'\badult|18\+\b'
            ]
        }
        
        # Risk assessment keywords
        self.risk_keywords = {
            'critical': ['child abuse', 'NCMEC', 'sexual content', 'illegal'],
            'high': ['minor safety', 'child protection', 'COPPA', 'parental consent'],
            'medium': ['GDPR', 'privacy', 'data protection', 'age verification'],
            'low': ['UI test', 'performance', 'analytics', 'optimization']
        }
        
        # Known regulatory frameworks
        self.regulations = {
            'GDPR': 'EU General Data Protection Regulation',
            'COPPA': 'US Children\'s Online Privacy Protection Act',
            'CCPA': 'California Consumer Privacy Act',
            'DSA': 'EU Digital Services Act',
            'Utah Social Media Regulation Act': 'Utah minor protection legislation',
            'SB976': 'California Age-Appropriate Design Code Act',
            'Florida Online Protections for Minors': 'Florida minor protection law'
        }
    
    def analyze_feature(self, title: str, description: str) -> Dict[str, Any]:
        """Analyze a single feature for geo-compliance requirements"""
        
        start_time = time.time()
        full_text = f"{title} {description}".lower()
        
        # Pattern matching
        high_conf_matches = sum(1 for pattern in self.compliance_patterns['high_confidence'] 
                               if re.search(pattern, full_text, re.IGNORECASE))
        
        medium_conf_matches = sum(1 for pattern in self.compliance_patterns['medium_confidence'] 
                                 if re.search(pattern, full_text, re.IGNORECASE))
        
        location_matches = sum(1 for pattern in self.compliance_patterns['location_indicators'] 
                              if re.search(pattern, full_text, re.IGNORECASE))
        
        age_matches = sum(1 for pattern in self.compliance_patterns['age_indicators'] 
                         if re.search(pattern, full_text, re.IGNORECASE))
        
        # Determine if geo-logic is needed
        needs_geo_logic = (high_conf_matches > 0 or 
                          (medium_conf_matches > 0 and location_matches > 0) or
                          (age_matches > 0 and location_matches > 0))
        
        # Calculate confidence
        confidence_score = min(1.0, (high_conf_matches * 0.4 + 
                                   medium_conf_matches * 0.2 + 
                                   location_matches * 0.15 + 
                                   age_matches * 0.15 + 0.1))
        
        # Determine risk assessment
        risk_level = 'low'
        for risk, keywords in self.risk_keywords.items():
            if any(keyword.lower() in full_text for keyword in keywords):
                risk_level = risk
                break
        
        # Extract applicable regulations using improved contextual detection
        applicable_regs = self._detect_regulations_contextual(full_text)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(title, description, high_conf_matches, 
                                           medium_conf_matches, location_matches, 
                                           age_matches, needs_geo_logic)
        
        # Extract locations and age terms
        detected_locations = self._extract_locations(full_text)
        detected_ages = self._extract_ages(full_text)
        
        # Calculate detailed confidence breakdowns
        entity_detection_confidence, entity_confidence_level = self._calculate_entity_detection_confidence(
            detected_locations, detected_ages, location_matches, age_matches)
        
        classification_confidence, classification_level = self._calculate_classification_confidence(
            high_conf_matches, medium_conf_matches, needs_geo_logic)
        
        law_matching_confidence, law_matching_level = self._calculate_law_matching_confidence(
            applicable_regs, full_text)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            'timestamp': datetime.now().isoformat(),
            'feature_name': title,
            'feature_description': description,
            'needs_geo_logic': needs_geo_logic,
            'primary_confidence': confidence_score,
            'secondary_confidence': confidence_score * 0.9,  # Slightly lower for secondary
            'overall_confidence': confidence_score,
            'reasoning': reasoning,
            'applicable_regulations': applicable_regs,
            'risk_assessment': risk_level,
            'regulatory_requirements': self._get_requirements(applicable_regs),
            'evidence_sources': [f"Pattern matching: {high_conf_matches + medium_conf_matches} matches"],
            'recommended_actions': self._get_recommendations(needs_geo_logic, risk_level),
            'detected_locations': detected_locations,
            'detected_ages': detected_ages,
            'pattern_matches': {
                'high_confidence': high_conf_matches,
                'medium_confidence': medium_conf_matches,
                'location_indicators': location_matches,
                'age_indicators': age_matches
            },
            'clear_cut_detection': high_conf_matches > 0,
            'needs_human_review': (medium_conf_matches > 0 and confidence_score < 0.7),
            'human_review_reason': 'Moderate confidence requires human validation' if (medium_conf_matches > 0 and confidence_score < 0.7) else '',
            'intervention_priority': 'high' if risk_level in ['critical', 'high'] else 'medium' if needs_geo_logic else 'low',
            'method_used': 'rule_based_pattern_matching',
            'processing_time_ms': processing_time,
            # Detailed confidence breakdowns
            'entity_detection_confidence': entity_detection_confidence,
            'entity_confidence_level': entity_confidence_level,
            'classification_confidence': classification_confidence,
            'classification_level': classification_level,
            'law_matching_confidence': law_matching_confidence,
            'law_matching_level': law_matching_level
        }
    
    def _detect_regulations_contextual(self, text: str) -> List[Dict[str, str]]:
        """Aggressive regulation detection using contextual analysis"""
        detected_regulations = []
        
        # EU - GDPR Detection (ANY EU mention triggers GDPR consideration)
        if re.search(r'\b(eu|european union|europe|eea)\b', text, re.IGNORECASE):
            detected_regulations.append({
                "name": "GDPR",
                "full_name": "EU General Data Protection Regulation",
                "jurisdiction": "EU",
                "relevance": "high",
                "reason": "EU jurisdiction requires GDPR compliance for data processing"
            })
        
        # US Federal Laws
        # COPPA Detection (US + children)
        if re.search(r'\b(us|usa|united states|america|federal)\b', text, re.IGNORECASE):
            if re.search(r'\b(child|under 13|minor|ncmec|child abuse|child sexual|coppa)\b', text, re.IGNORECASE):
                detected_regulations.append({
                    "name": "COPPA",
                    "full_name": "US Children's Online Privacy Protection Act",
                    "jurisdiction": "US",
                    "relevance": "high",
                    "reason": "US jurisdiction with children context"
                })
        
        # NCMEC Reporting (US Federal)
        if re.search(r'\b(ncmec|child abuse|sexual abuse|child sexual|federal law|report.*child)\b', text, re.IGNORECASE):
            detected_regulations.append({
                "name": "US Federal NCMEC Reporting",
                "full_name": "US Federal law requiring NCMEC reporting",
                "jurisdiction": "US",
                "relevance": "critical",
                "reason": "Child abuse content reporting requirements"
            })
        
        # California Laws (SB976/CCPA)
        if re.search(r'\b(california)\b', text, re.IGNORECASE):
            if re.search(r'\bsb976\b', text, re.IGNORECASE):
                detected_regulations.append({
                    "name": "SB976",
                    "full_name": "California Age-Appropriate Design Code Act",
                    "jurisdiction": "California",
                    "relevance": "high",
                    "reason": "Explicit SB976 mention"
                })
            elif re.search(r'\b(teen|minor|under 18|privacy|personalization|ccpa)\b', text, re.IGNORECASE):
                detected_regulations.append({
                    "name": "CCPA/SB976",
                    "full_name": "California Consumer Privacy Act / Age-Appropriate Design Code",
                    "jurisdiction": "California",
                    "relevance": "medium",
                    "reason": "California jurisdiction with minor privacy context"
                })
        
        # Utah Law
        if re.search(r'\butah\b', text, re.IGNORECASE):
            detected_regulations.append({
                "name": "Utah Social Media Regulation Act",
                "full_name": "Utah minor protection legislation",
                "jurisdiction": "Utah",
                "relevance": "high",
                "reason": "Utah jurisdiction with social media context"
            })
        
        # Florida Law
        if re.search(r'\bflorida\b', text, re.IGNORECASE):
            detected_regulations.append({
                "name": "Florida Online Protections for Minors",
                "full_name": "Florida minor protection law",
                "jurisdiction": "Florida",
                "relevance": "high",
                "reason": "Florida jurisdiction with minor protection context"
            })
        
        # Canada - PIPEDA
        if re.search(r'\b(canada|canadian)\b', text, re.IGNORECASE):
            detected_regulations.append({
                "name": "PIPEDA",
                "full_name": "Personal Information Protection and Electronic Documents Act",
                "jurisdiction": "Canada",
                "relevance": "medium",
                "reason": "Canadian jurisdiction requires PIPEDA compliance"
            })
        
        # South Korea - Personal Information Protection Act
        if re.search(r'\b(south korea|korea)\b', text, re.IGNORECASE):
            detected_regulations.append({
                "name": "South Korea PIPA",
                "full_name": "Personal Information Protection Act",
                "jurisdiction": "South Korea",
                "relevance": "medium",
                "reason": "South Korean jurisdiction requires PIPA compliance"
            })
        
        # Age-based Features - ALWAYS apply minor protection laws
        if re.search(r'\b(age.*based|age.*specific|age.*verification|minor|child|teen|under 1[3-8]|underage)\b', text, re.IGNORECASE):
            # Check if we don't already have jurisdiction-specific minor protection laws
            existing_minor_laws = [reg.get('name', '') for reg in detected_regulations 
                                 if 'minor' in reg.get('full_name', '').lower() or 
                                    reg.get('name', '') in ['COPPA', 'SB976', 'Utah Social Media Regulation Act', 'Florida Online Protections for Minors']]
            
            if not existing_minor_laws:
                detected_regulations.append({
                    "name": "General Minor Protection Laws",
                    "full_name": "Various age-appropriate design and safety regulations",
                    "jurisdiction": "Multiple",
                    "relevance": "medium",
                    "reason": "Age-related functionality requires minor protection compliance"
                })
        
        # Regional A/B Testing - Data Protection Considerations
        if re.search(r'\b(region|regional|location|geographic|targeting|test.*region|rollout.*region)\b', text, re.IGNORECASE):
            if not any(reg.get('jurisdiction', '') in ['EU', 'US', 'California', 'Canada', 'South Korea'] for reg in detected_regulations):
                detected_regulations.append({
                    "name": "Regional Data Protection Laws",
                    "full_name": "Regional data protection and privacy regulations",
                    "jurisdiction": "Multiple",
                    "relevance": "medium",
                    "reason": "Regional targeting requires local data protection compliance"
                })
        
        # Content Moderation and Safety
        if re.search(r'\b(content|filter|flag|moderate|safety|protection)\b', text, re.IGNORECASE):
            if re.search(r'\b(minor|child|inappropriate|adult.*themed)\b', text, re.IGNORECASE):
                if not any('Minor Protection' in reg.get('name', '') for reg in detected_regulations):
                    detected_regulations.append({
                        "name": "Child Safety Regulations",
                        "full_name": "Child online safety and content filtering requirements",
                        "jurisdiction": "Multiple",
                        "relevance": "medium",
                        "reason": "Child safety content filtering requires compliance with minor protection laws"
                    })
        
        return detected_regulations
    
    def _get_jurisdiction(self, regulation: str) -> str:
        """Get jurisdiction for a regulation"""
        jurisdiction_map = {
            'GDPR': 'EU',
            'DSA': 'EU', 
            'COPPA': 'US',
            'CCPA': 'California',
            'SB976': 'California',
            'Utah Social Media Regulation Act': 'Utah',
            'Florida Online Protections for Minors': 'Florida'
        }
        return jurisdiction_map.get(regulation, 'Unknown')
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extract location mentions from text"""
        locations = []
        location_patterns = {
            'US': r'\b(US|USA|United States|America)\b',
            'EU': r'\b(EU|European Union|Europe)\b',
            'California': r'\b(CA|California|Calif)\b',
            'Utah': r'\bUtah\b',
            'Florida': r'\bFlorida\b',
            'Canada': r'\b(Canada|Canadian)\b'
        }
        
        for location, pattern in location_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                locations.append(location)
        
        return locations
    
    def _extract_ages(self, text: str) -> List[str]:
        """Extract age-related terms from text"""
        ages = []
        age_patterns = [
            (r'\bunder (\d+)\b', lambda m: f'under {m.group(1)}'),
            (r'\b(\d+) and up\b', lambda m: f'{m.group(1)}+'),
            (r'\bminor\b', lambda m: 'minor'),
            (r'\bchild\b', lambda m: 'child'),
            (r'\bteen\b', lambda m: 'teen')
        ]
        
        for pattern, formatter in age_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ages.append(formatter(match))
        
        return list(set(ages))  # Remove duplicates
    
    def _generate_reasoning(self, title: str, description: str, high_matches: int, 
                          medium_matches: int, location_matches: int, age_matches: int, 
                          needs_geo: bool) -> str:
        """Generate human-readable reasoning"""
        
        if high_matches > 0:
            reason = f"Feature contains explicit compliance indicators ({high_matches} matches) "
        elif medium_matches > 0 and location_matches > 0:
            reason = f"Feature shows geographic restrictions with compliance context ({medium_matches} compliance + {location_matches} location matches) "
        elif age_matches > 0 and location_matches > 0:
            reason = f"Feature targets specific age groups in specific locations ({age_matches} age + {location_matches} location matches) "
        else:
            reason = "Feature appears to be business-focused without clear regulatory requirements "
        
        if needs_geo:
            reason += "suggesting geo-specific compliance logic is required."
        else:
            reason += "indicating no specialized geo-compliance logic needed."
        
        return reason
    
    def _get_requirements(self, regulations: List[Dict]) -> List[str]:
        """Get regulatory requirements"""
        requirements = []
        for reg in regulations:
            reg_name = reg['name']
            if reg_name == 'GDPR':
                requirements.append('Age verification for users under 16')
                requirements.append('Parental consent mechanisms')
            elif reg_name == 'COPPA':
                requirements.append('Parental consent for users under 13')
                requirements.append('Limited data collection from minors')
            elif reg_name in ['Utah Social Media Regulation Act']:
                requirements.append('Curfew enforcement for minors')
                requirements.append('Parental notification systems')
            elif reg_name == 'DSA':
                requirements.append('Content transparency reporting')
                requirements.append('Risk assessment for minors')
        
        return requirements or ['Standard platform policies apply']
    
    def _get_recommendations(self, needs_geo: bool, risk_level: str) -> List[str]:
        """Get recommended actions"""
        recommendations = []
        
        if needs_geo:
            recommendations.append('Implement geo-location detection')
            recommendations.append('Configure region-specific feature flags')
            
        if risk_level in ['critical', 'high']:
            recommendations.append('Prioritize legal review')
            recommendations.append('Implement additional safeguards')
        elif risk_level == 'medium':
            recommendations.append('Consider legal consultation')
            recommendations.append('Document compliance approach')
        else:
            recommendations.append('Standard feature deployment process')
        
        return recommendations
    
    def _calculate_entity_detection_confidence(self, detected_locations: List[str], 
                                             detected_ages: List[str], 
                                             location_matches: int, 
                                             age_matches: int) -> Tuple[float, str]:
        """Calculate confidence for entity detection"""
        
        # Base confidence from pattern matches
        base_confidence = min(1.0, (location_matches * 0.25 + age_matches * 0.25 + 0.2))
        
        # Boost for actual entity extraction
        entity_boost = 0.0
        if detected_locations:
            entity_boost += 0.2 * len(detected_locations)
        if detected_ages:
            entity_boost += 0.2 * len(detected_ages)
        
        # Final confidence calculation
        confidence = min(1.0, base_confidence + entity_boost)
        
        # Determine confidence level
        if confidence >= 0.8:
            level = "High"
        elif confidence >= 0.5:
            level = "Medium" 
        else:
            level = "Low"
        
        return confidence, level
    
    def _calculate_classification_confidence(self, high_conf_matches: int, 
                                           medium_conf_matches: int, 
                                           needs_geo_logic: bool) -> Tuple[float, str]:
        """Calculate confidence for classification accuracy"""
        
        # High confidence if we have strong pattern matches
        if high_conf_matches > 0:
            confidence = min(1.0, 0.7 + (high_conf_matches * 0.15))
        elif medium_conf_matches > 0:
            confidence = min(1.0, 0.5 + (medium_conf_matches * 0.1))
        else:
            confidence = 0.4
        
        # Boost if geo-logic determination is clear
        if needs_geo_logic or (high_conf_matches == 0 and medium_conf_matches == 0):
            confidence += 0.15
        
        confidence = min(1.0, confidence)
        
        # Determine confidence level
        if confidence >= 0.85:
            level = "High"
        elif confidence >= 0.6:
            level = "Medium"
        else:
            level = "Low"
        
        return confidence, level
    
    def _calculate_law_matching_confidence(self, applicable_regs: List[Dict], 
                                         full_text: str) -> Tuple[float, str]:
        """Calculate confidence for law matching accuracy"""
        
        if not applicable_regs:
            # No regulations detected - could be accurate or missed
            # Check if text has strong regulatory indicators
            regulatory_terms = len(re.findall(r'\b(law|regulation|compliance|legal|jurisdiction|act)\b', 
                                            full_text, re.IGNORECASE))
            if regulatory_terms > 0:
                confidence = 0.3  # Low confidence - might have missed something
            else:
                confidence = 0.8  # High confidence - likely no regulations needed
        else:
            # Regulations detected - assess confidence based on specificity
            confidence = 0.5  # Base confidence
            
            for reg in applicable_regs:
                relevance = reg.get('relevance', 'medium')
                reason = reg.get('reason', '')
                
                # Boost for high relevance
                if relevance == 'critical':
                    confidence += 0.25
                elif relevance == 'high':
                    confidence += 0.15
                elif relevance == 'medium':
                    confidence += 0.1
                
                # Boost for specific reasoning
                if 'explicit' in reason.lower() or 'specific' in reason.lower():
                    confidence += 0.1
                elif 'jurisdiction' in reason.lower():
                    confidence += 0.05
        
        confidence = min(1.0, confidence)
        
        # Determine confidence level
        if confidence >= 0.75:
            level = "High"
        elif confidence >= 0.45:
            level = "Medium"
        else:
            level = "Low"
        
        return confidence, level

def process_features(input_csv: str, output_csv: str):
    """Process all features and save results"""
    
    print("🚀 Starting Simple Feature Analysis")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = SimpleFeatureAnalyzer()
    
    # Read features
    print(f"📖 Reading features from: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"✅ Found {len(df)} features to analyze")
    print()
    
    results = []
    
    for i, row in df.iterrows():
        feature_name = str(row['feature_name']) if pd.notna(row['feature_name']) else ""
        feature_description = str(row['feature_description']) if pd.notna(row['feature_description']) else ""
        
        print(f"🔍 Analyzing Feature {i+1}/{len(df)}: {feature_name[:50]}...")
        
        try:
            result = analyzer.analyze_feature(feature_name, feature_description)
            results.append(result)
            
            # Show status
            status = "✅ Clear-cut" if result['clear_cut_detection'] else f"🔍 {result['overall_confidence']:.1%} confidence"
            geo_status = "🌍 Geo-logic needed" if result['needs_geo_logic'] else "🏠 No geo-logic"
            risk_status = f"📊 Risk: {result['risk_assessment']}"
            
            print(f"  {status} | {geo_status} | {risk_status}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            # Add error result
            results.append({
                'timestamp': datetime.now().isoformat(),
                'feature_name': feature_name,
                'feature_description': feature_description,
                'needs_geo_logic': None,
                'primary_confidence': 0.0,
                'secondary_confidence': 0.0,
                'overall_confidence': 0.0,
                'reasoning': f"Processing error: {str(e)}",
                'applicable_regulations': [],
                'risk_assessment': 'error',
                'regulatory_requirements': [],
                'evidence_sources': [],
                'recommended_actions': [],
                'detected_locations': [],
                'detected_ages': [],
                'pattern_matches': {},
                'clear_cut_detection': False,
                'needs_human_review': True,
                'human_review_reason': f"Processing error: {str(e)}",
                'intervention_priority': 'high',
                'method_used': 'error',
                'processing_time_ms': 0.0
            })
    
    # Convert to DataFrame and save
    print(f"\n💾 Saving results to: {output_csv}")
    results_df = pd.DataFrame(results)
    
    # Flatten complex fields for CSV
    results_df['applicable_regulations'] = results_df['applicable_regulations'].apply(lambda x: json.dumps(x) if isinstance(x, list) else str(x))
    results_df['regulatory_requirements'] = results_df['regulatory_requirements'].apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
    results_df['evidence_sources'] = results_df['evidence_sources'].apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
    results_df['recommended_actions'] = results_df['recommended_actions'].apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
    results_df['detected_locations'] = results_df['detected_locations'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
    results_df['detected_ages'] = results_df['detected_ages'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
    results_df['pattern_matches'] = results_df['pattern_matches'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else str(x))
    
    results_df.to_csv(output_csv, index=False)
    
    # Print summary
    print("\n📊 ANALYSIS SUMMARY")
    print("=" * 60)
    
    total = len(results)
    geo_needed = sum(1 for r in results if r.get('needs_geo_logic') == True)
    clear_cut = sum(1 for r in results if r.get('clear_cut_detection') == True)
    human_review = sum(1 for r in results if r.get('needs_human_review') == True)
    
    print(f"📋 Total Features: {total}")
    print(f"🌍 Geo-logic Required: {geo_needed}")
    print(f"⚡ Clear-cut Cases: {clear_cut}")
    print(f"🚨 Human Review Required: {human_review}")
    
    # Risk breakdown
    risk_counts = {}
    for result in results:
        risk = result.get('risk_assessment', 'unknown')
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    print(f"\n📈 Risk Levels:")
    for risk, count in sorted(risk_counts.items()):
        print(f"  {risk.title()}: {count}")
    
    print(f"\n✅ Results saved to: {output_csv}")
    print("🚀 Analysis Complete!")
    
    return results_df

if __name__ == "__main__":
    input_file = "input_features.csv"
    output_file = "feature_analysis_results.csv"
    
    try:
        process_features(input_file, output_file)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
