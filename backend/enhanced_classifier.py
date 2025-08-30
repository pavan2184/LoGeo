"""
Enhanced Multi-Stage Classification System for Geo-Compliance

This module implements the complete feature flow:
1. Preprocessing and NER/Regex detection (95% confidence cases)
2. Entity standardization with glossary 
3. Multi-stage classification with LLM + cross-checking
4. Confidence calculation with category-specific thresholds
5. Human intervention alerts for low confidence cases
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from backend.preprocessing import get_preprocessor, PreprocessingResult, EntityMatch
from backend.glossary import get_glossary, LocationMapping, AgeMapping, TerminologyMapping, EscalationDecision
from backend.llm_classifier import get_classifier, RegulatoryAnalysisResult
from backend.rag_loader import get_rag_instance
from backend.confidence_scoring import get_confidence_scorer, ConfidenceBreakdown, ConfidenceLevel
from backend.ambiguity_handler import get_ambiguity_handler, AmbiguityAssessment, DisambiguationResult

logger = logging.getLogger(__name__)

@dataclass
class StandardizedEntities:
    """Standardized entities extracted from text"""
    locations: List[Dict[str, Any]]  # Standardized location information
    ages: List[Dict[str, Any]]       # Standardized age information  
    terminology: List[Dict[str, Any]] # Standardized regulatory terminology
    confidence_scores: Dict[str, float]  # Confidence by category

@dataclass
class EnhancedClassificationResult:
    """Complete classification result with all confidence metrics"""
    # Core classification
    needs_geo_logic: bool
    primary_confidence: float  # LLM confidence
    secondary_confidence: float  # Regex/NER confidence  
    overall_confidence: float  # Combined confidence
    
    # Detailed analysis
    reasoning: str
    applicable_regulations: List[dict]
    risk_assessment: str
    regulatory_requirements: List[str]
    evidence_sources: List[str]
    recommended_actions: List[str]
    
    # Enhanced features
    standardized_entities: StandardizedEntities
    preprocessing_result: PreprocessingResult
    clear_cut_detection: bool
    confidence_breakdown: Dict[str, float]
    
    # Human intervention
    needs_human_review: bool
    human_review_reason: str
    intervention_priority: str  # "low", "medium", "high", "critical"
    
    # Audit trail
    processing_timestamp: str
    method_used: str  # "clear_cut", "llm_primary", "llm_secondary", "rule_based"
    processing_time_ms: float
    
    # Optional fields with defaults (must come last)
    detailed_confidence: Optional[ConfidenceBreakdown] = None
    ambiguity_assessments: Optional[List[AmbiguityAssessment]] = None
    disambiguation_result: Optional[DisambiguationResult] = None
    ambiguity_confidence_penalty: float = 0.0
    threshold_decision: Optional[EscalationDecision] = None
    final_action: str = ""  # "auto_approve", "human_review", "ignore"

class EnhancedGeoComplianceClassifier:
    """
    Enhanced classifier implementing the complete multi-stage feature flow.
    Combines preprocessing, NER, LLM analysis, and confidence calculation.
    """
    
    def __init__(self):
        self.preprocessor = get_preprocessor()
        self.glossary = get_glossary()
        self.llm_classifier = get_classifier()
        self.rag = get_rag_instance()
        self.confidence_scorer = get_confidence_scorer()
        self.ambiguity_handler = get_ambiguity_handler()
        
        # Legacy confidence thresholds (kept for backward compatibility)
        self.confidence_thresholds = {
            "minor_protection": 0.90,   # Higher threshold for child safety
            "content_safety": 0.90,    # Higher threshold for CSAM/abuse
            "privacy_rights": 0.85,    # High threshold for privacy
            "data_protection": 0.85,   # High threshold for data handling
            "general_compliance": 0.80, # Standard threshold
            "business_feature": 0.75   # Lower threshold for business decisions
        }
        
        # Updated category determination keywords aligned with threshold rules
        self.category_keywords = {
            # Legal/Compliance categories (threshold: 0.90)
            "minor_protection": ["minor", "child", "teen", "age", "parental", "youth", "juvenile", "underage", "coppa", "age verification"],
            "content_safety": ["csam", "abuse", "harm", "exploitation", "safety", "ncmec", "reporting", "child sexual abuse"],
            "privacy_rights": ["privacy", "data", "personal", "tracking", "collection", "consent", "gdpr", "ccpa"],
            "data_protection": ["data protection", "localization", "retention", "data residency", "cross-border"],
            "regulatory_compliance": ["compliance", "regulation", "law", "legal", "requirement", "dsa", "digital services act"],
            
            # Safety/Health Protection categories (threshold: 0.85)
            "user_safety": ["safety", "harm prevention", "user protection", "content moderation", "community standards"],
            "health_protection": ["health", "mental health", "wellbeing", "addiction", "time limits"],
            "harm_prevention": ["harmful content", "violence", "self-harm", "dangerous", "risk assessment"],
            "security_compliance": ["security", "authentication", "access control", "identity verification"],
            
            # Business (non-binding) categories (threshold: 0.70)
            "business_feature": ["feature", "functionality", "product", "user interface", "ui", "ux"],
            "market_testing": ["test", "experiment", "rollout", "market", "pilot", "beta", "a/b test"],
            "user_experience": ["experience", "engagement", "usability", "interface", "design"],
            "performance_optimization": ["performance", "optimization", "speed", "efficiency", "revenue", "conversion"],
            
            # Internal Analytics categories (threshold: 0.60)
            "analytics": ["analytics", "data analysis", "tracking", "measurement", "insights"],
            "metrics": ["metrics", "kpi", "statistics", "reporting", "dashboard"],
            "internal_monitoring": ["monitoring", "logging", "debugging", "internal", "observability"],
            "development_tools": ["development", "tools", "testing", "staging", "dev", "tooling"]
        }
    
    def standardize_entities(self, entities: List[EntityMatch]) -> StandardizedEntities:
        """
        Standardize all detected entities using the glossary system.
        This implements the Location/Age/Terminology standardization from the feature flow.
        """
        
        standardized_locations = []
        standardized_ages = []
        standardized_terminology = []
        
        confidence_scores = {"location": 0.0, "age": 0.0, "terminology": 0.0}
        
        for entity in entities:
            if entity.entity_type == "LOCATION":
                location, conf = self.glossary.standardize_location(entity.text)
                if location:
                    standardized_locations.append({
                        "original_text": entity.text,
                        "colloquial_name": location.colloquial_name,
                        "full_name": location.full_name,
                        "country_code": location.country_code_iso,
                        "region": location.region,
                        "confidence": conf,
                        "source": entity.source
                    })
                    confidence_scores["location"] = max(confidence_scores["location"], conf)
            
            elif entity.entity_type == "AGE":
                age, conf = self.glossary.standardize_age(entity.text)
                if age:
                    standardized_ages.append({
                        "original_text": entity.text,
                        "standardized_term": age.term,
                        "numerical_range": age.numerical_range,
                        "confidence": conf,
                        "source": entity.source
                    })
                    confidence_scores["age"] = max(confidence_scores["age"], conf)
            
            elif entity.entity_type == "TERMINOLOGY":
                term, conf = self.glossary.standardize_terminology(entity.text)
                if term:
                    standardized_terminology.append({
                        "original_text": entity.text,
                        "standardized_form": term.standardized_form,
                        "category": term.category,
                        "confidence": conf,
                        "source": entity.source
                    })
                    confidence_scores["terminology"] = max(confidence_scores["terminology"], conf)
        
        return StandardizedEntities(
            locations=standardized_locations,
            ages=standardized_ages,
            terminology=standardized_terminology,
            confidence_scores=confidence_scores
        )
    
    def process_ambiguity(self, 
                         entities: List[EntityMatch], 
                         text: str,
                         feature_category: str) -> Tuple[List[AmbiguityAssessment], Optional[DisambiguationResult], float]:
        """
        Process ambiguity in detected entities and apply resolution strategies.
        
        Args:
            entities: List of detected entities from preprocessing
            text: Original text being analyzed
            feature_category: Category of the feature for context
        
        Returns:
            Tuple of (ambiguity_assessments, disambiguation_result, confidence_penalty)
        """
        
        # Convert entities to format expected by ambiguity handler
        entity_dicts = []
        for entity in entities:
            entity_dicts.append({
                "entity_type": entity.entity_type,
                "text": entity.text,
                "source": entity.source,
                "confidence": entity.confidence
            })
        
        # Prepare context for ambiguity assessment
        context = {
            "feature_category": feature_category,
            "text_length": len(text),
            "has_regulatory_signals": any(signal in text.lower() for signal in 
                                        ["gdpr", "ccpa", "coppa", "dsa", "law", "regulation", "compliance"])
        }
        
        # Assess ambiguity
        ambiguity_assessments = self.ambiguity_handler.assess_ambiguity(
            entity_dicts, text, context
        )
        
        # Resolve ambiguities if any detected
        disambiguation_result = None
        confidence_penalty = 0.0
        
        if ambiguity_assessments:
            disambiguation_result = self.ambiguity_handler.resolve_ambiguities(
                ambiguity_assessments, use_defaults=True
            )
            confidence_penalty = disambiguation_result.overall_confidence_penalty
            
            logger.info(f"Processed {len(ambiguity_assessments)} ambiguities with {confidence_penalty:.3f} confidence penalty")
        
        return ambiguity_assessments, disambiguation_result, confidence_penalty
    
    def determine_feature_category(self, text: str, entities: StandardizedEntities) -> str:
        """Determine the primary category of the feature for appropriate thresholding"""
        
        text_lower = text.lower()
        category_scores = {}
        
        # Score based on keywords
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = score
        
        # Boost scores based on standardized entities
        if entities.ages:
            category_scores["minor_protection"] = category_scores.get("minor_protection", 0) + 3
        
        if any("safety" in term["category"] for term in entities.terminology):
            category_scores["content_safety"] = category_scores.get("content_safety", 0) + 3
        
        if any("privacy" in term["category"] for term in entities.terminology):
            category_scores["privacy_rights"] = category_scores.get("privacy_rights", 0) + 3
        
        if any("content_moderation" in term["category"] for term in entities.terminology):
            category_scores["user_safety"] = category_scores.get("user_safety", 0) + 2
        
        # Return category with highest score
        if category_scores and max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        
        # Default to regulatory_compliance for safety
        return "regulatory_compliance"
    
    def build_enhanced_prompt(self, title: str, description: str, entities: StandardizedEntities, rag_context: str) -> str:
        """
        Build enhanced prompt with standardized entities for better LLM classification.
        This implements the prompt engineering aspect of the feature flow.
        """
        
        # Build entity context
        entity_context = []
        
        if entities.locations:
            locations_text = ", ".join([f"{loc['colloquial_name']} ({loc['country_code']})" for loc in entities.locations])
            entity_context.append(f"DETECTED LOCATIONS: {locations_text}")
        
        if entities.ages:
            ages_text = ", ".join([f"{age['standardized_term']} (ages {age['numerical_range'][0]}-{age['numerical_range'][1]})" for age in entities.ages])
            entity_context.append(f"DETECTED AGE TERMS: {ages_text}")
        
        if entities.terminology:
            terms_text = ", ".join([f"{term['standardized_form']} ({term['category']})" for term in entities.terminology])
            entity_context.append(f"DETECTED REGULATORY TERMS: {terms_text}")
        
        entity_section = "\n".join(entity_context) if entity_context else "No specific entities detected."
        
        prompt = f"""
You are a senior regulatory compliance expert analyzing software features for geographic-specific legal requirements.

FEATURE TO ANALYZE:
Title: {title}
Description: {description}

STANDARDIZED ENTITY ANALYSIS:
{entity_section}

RELEVANT REGULATORY CONTEXT:
{rag_context}

ENHANCED ANALYSIS REQUIREMENTS:
Based on the standardized entities and regulatory context, determine:

1. GEOTAGGING NECESSITY: Does this feature require geographic-specific implementation due to legal requirements?
   - Consider the specific locations, age groups, and regulatory terms detected
   - Distinguish between legal compliance requirements vs. business decisions
   - If locations are detected, assess whether they indicate legal jurisdiction requirements

2. CONFIDENCE ASSESSMENT: Provide detailed confidence scoring:
   - Entity detection confidence: How certain are you about the extracted entities?
   - Regulatory requirement confidence: How certain are you about legal obligations?
   - Geographic necessity confidence: How certain are you about geo-specific requirements?

3. CROSS-VALIDATION: Validate against multiple regulatory sources:
   - Primary assessment based on detected regulatory terms
   - Secondary assessment based on location and age combinations
   - Cross-check against known compliance patterns

RESPONSE FORMAT (JSON):
{{
    "needs_geo_logic": true/false,
    "confidence": 0.95,
    "reasoning": "Detailed analysis incorporating standardized entities...",
    "applicable_regulations": [
        {{
            "name": "Regulation Name",
            "jurisdiction": "Geographic Scope",
            "relevance": "high/medium/low",
            "specific_articles": ["Article X"],
            "legal_basis": "Why this regulation applies",
            "detected_entities": ["relevant entities that triggered this"]
        }}
    ],
    "risk_assessment": "high/medium/low",
    "regulatory_requirements": ["Specific legal obligations"],
    "evidence_sources": ["Sources supporting this analysis"],
    "recommended_actions": ["Specific next steps"],
    "entity_validation": {{
        "location_confidence": 0.95,
        "age_confidence": 0.90,
        "terminology_confidence": 0.85
    }},
    "cross_validation_score": 0.92
}}

CRITICAL INSTRUCTIONS:
- Use the standardized entities to inform your analysis
- Cross-reference detected locations with known regulatory jurisdictions
- Consider age-related entities for minor protection laws
- Validate terminology against known compliance requirements
- Provide specific confidence scores for different aspects
- Flag any uncertainties that might require human review
"""
        
        return prompt
    
    def cross_validate_with_secondary_checks(self, 
                                           text: str, 
                                           llm_result: RegulatoryAnalysisResult,
                                           entities: StandardizedEntities) -> Tuple[float, Dict[str, float]]:
        """
        Perform enhanced secondary validation using regex/NER patterns.
        This implements the improved Primary + Secondary cross-checking with weighted scoring.
        """
        
        secondary_scores = {
            "location_validation": 0.0,
            "age_validation": 0.0, 
            "terminology_validation": 0.0,
            "pattern_matching": 0.0,
            "regulatory_alignment": 0.0
        }
        
        # Enhanced location validation with jurisdiction alignment
        if entities.locations:
            detected_jurisdictions = [loc["region"] for loc in entities.locations]
            llm_jurisdictions = [reg.get("jurisdiction", "") for reg in llm_result.applicable_regulations]
            
            # Calculate jurisdiction overlap score
            jurisdiction_matches = 0
            total_checks = len(detected_jurisdictions) * len(llm_jurisdictions) if llm_jurisdictions else 1
            
            for det_regions in detected_jurisdictions:
                for llm_jurisdiction in llm_jurisdictions:
                    if any(region.lower() in llm_jurisdiction.lower() for region in det_regions):
                        jurisdiction_matches += 1
            
            jurisdiction_score = jurisdiction_matches / total_checks if total_checks > 0 else 0.0
            secondary_scores["location_validation"] = min(jurisdiction_score + 0.6, 0.95)
        
        # Enhanced age validation with regulation specificity
        if entities.ages:
            age_regulations = ["coppa", "minor protection", "parental consent", "age verification", "children"]
            regulation_text = " ".join([reg.get("name", "") + " " + llm_result.reasoning for reg in llm_result.applicable_regulations])
            
            age_mentions = sum(1 for age_reg in age_regulations if age_reg in regulation_text.lower())
            age_score = min(age_mentions * 0.3 + 0.5, 0.95)
            secondary_scores["age_validation"] = age_score
        
        # Enhanced terminology validation with category alignment
        if entities.terminology:
            detected_categories = set(term["category"] for term in entities.terminology)
            
            # Check category alignment with LLM reasoning and regulations
            category_alignment = 0
            for category in detected_categories:
                if category in llm_result.reasoning.lower():
                    category_alignment += 0.3
                for reg in llm_result.applicable_regulations:
                    if category in reg.get("name", "").lower() or category in reg.get("legal_basis", "").lower():
                        category_alignment += 0.2
            
            secondary_scores["terminology_validation"] = min(category_alignment + 0.4, 0.95)
        
        # Enhanced pattern matching with regulatory context
        compliance_patterns = [
            r'\b(?:comply|compliance)\s+with.*(?:law|regulation|act)\b',
            r'\b(?:geo.*restriction|geographic.*requirement|location.*based.*compliance)\b',
            r'\b(?:minor.*protection|age.*verification|parental.*consent).*(?:law|requirement)\b',
            r'\b(?:data.*protection|privacy.*law|gdpr|ccpa|dsa)\b',
            r'\b(?:content.*moderation|harmful.*content|safety.*requirement)\b'
        ]
        
        import re
        pattern_matches = sum(1 for pattern in compliance_patterns if re.search(pattern, text, re.IGNORECASE))
        secondary_scores["pattern_matching"] = min(pattern_matches * 0.2 + 0.3, 0.9)
        
        # New: Regulatory alignment validation
        if llm_result.applicable_regulations:
            # Check if risk assessment aligns with detected entities
            risk_entity_alignment = 0.5  # Base score
            
            if entities.ages and llm_result.risk_assessment in ["high", "critical"]:
                risk_entity_alignment += 0.2
            if entities.locations and len(llm_result.applicable_regulations) > 1:
                risk_entity_alignment += 0.2
            if entities.terminology and any("privacy" in term["category"] for term in entities.terminology):
                risk_entity_alignment += 0.1
                
            secondary_scores["regulatory_alignment"] = min(risk_entity_alignment, 0.95)
        
        # Calculate weighted secondary confidence (improved logic)
        weights = {
            "location_validation": 0.25,
            "age_validation": 0.25,
            "terminology_validation": 0.25,
            "pattern_matching": 0.15,
            "regulatory_alignment": 0.10
        }
        
        overall_secondary = sum(score * weights[category] for category, score in secondary_scores.items())
        
        return overall_secondary, secondary_scores
    
    def calculate_enhanced_confidence(self, 
                                    primary_confidence: float,
                                    secondary_confidence: float, 
                                    entities: StandardizedEntities,
                                    feature_category: str,
                                    cross_validation_scores: Dict[str, float]) -> ConfidenceBreakdown:
        """
        Calculate final confidence using the new standardized confidence scoring system.
        This replaces the old calculate_final_confidence method with systematic weighted scoring.
        """
        
        # Calculate entity quality score
        entity_quality = sum(entities.confidence_scores.values()) / len(entities.confidence_scores) if entities.confidence_scores else 0.5
        
        # Calculate cross-validation score from secondary checks
        cross_validation_confidence = sum(cross_validation_scores.values()) / len(cross_validation_scores) if cross_validation_scores else 0.5
        
        # Determine diversity factors
        diversity_factors = {
            "has_locations": bool(entities.locations),
            "has_ages": bool(entities.ages),
            "has_terminology": bool(entities.terminology),
            "has_cross_validation": cross_validation_confidence > 0.6
        }
        
        # Use the standardized confidence scorer
        confidence_breakdown = self.confidence_scorer.calculate_weighted_confidence(
            llm_score=primary_confidence,
            regex_ner_score=secondary_confidence,
            entity_quality=entity_quality,
            cross_validation_score=cross_validation_confidence,
            diversity_factors=diversity_factors
        )
        
        return confidence_breakdown
    
    def apply_ambiguity_penalty(self, 
                               confidence_breakdown: ConfidenceBreakdown,
                               ambiguity_penalty: float) -> ConfidenceBreakdown:
        """Apply ambiguity penalty to confidence breakdown"""
        
        # Apply penalty to final confidence
        adjusted_confidence = max(0.0, confidence_breakdown.final_confidence - ambiguity_penalty)
        
        # Update confidence factors
        updated_factors = confidence_breakdown.confidence_factors.copy()
        updated_factors["ambiguity_penalty"] = -ambiguity_penalty
        updated_factors["adjusted_final_confidence"] = adjusted_confidence
        
        # Update recommendations
        updated_recommendations = confidence_breakdown.recommendations.copy()
        if ambiguity_penalty > 0.2:
            updated_recommendations.insert(0, "High ambiguity detected - consider human review")
        elif ambiguity_penalty > 0.1:
            updated_recommendations.insert(0, "Moderate ambiguity detected - proceed with caution")
        
        # Return updated confidence breakdown
        return ConfidenceBreakdown(
            llm_confidence=confidence_breakdown.llm_confidence,
            regex_ner_confidence=confidence_breakdown.regex_ner_confidence,
            entity_confidence=confidence_breakdown.entity_confidence,
            cross_validation_confidence=confidence_breakdown.cross_validation_confidence,
            final_confidence=adjusted_confidence,
            confidence_level=self.confidence_scorer.classify_confidence_level(adjusted_confidence),
            confidence_factors=updated_factors,
            recommendations=updated_recommendations
        )
    
    def determine_threshold_based_action(self, 
                                       confidence: float,
                                       feature_category: str,
                                       entities: StandardizedEntities,
                                       llm_result: RegulatoryAnalysisResult) -> Tuple[EscalationDecision, bool, str, str, str]:
        """
        Determine action based on new threshold table system.
        Returns: (threshold_decision, needs_human_review, review_reason, priority, final_action)
        """
        
        # Use the threshold table system to evaluate
        threshold_decision = self.glossary.evaluate_threshold(feature_category, confidence)
        
        # Determine final action based on threshold decision
        if threshold_decision.escalation_action == "auto_approve":
            return threshold_decision, False, "", "low", "auto_approve"
        
        elif threshold_decision.escalation_action == "ignore":
            return threshold_decision, False, "", "low", "ignore"
        
        elif threshold_decision.escalation_action == "human_review":
            return threshold_decision, True, threshold_decision.reasoning, threshold_decision.priority, "human_review"
        
        else:
            # Additional checks for edge cases (keep existing logic)
            needs_review, reason, priority = self._additional_intervention_checks(
                confidence, feature_category, entities, llm_result
            )
            
            if needs_review:
                return threshold_decision, True, reason, priority, "human_review"
            else:
                return threshold_decision, False, "", "low", "auto_approve"
    
    def _additional_intervention_checks(self, 
                                      confidence: float,
                                      feature_category: str,
                                      entities: StandardizedEntities,
                                      llm_result: RegulatoryAnalysisResult) -> Tuple[bool, str, str]:
        """
        Additional intervention checks beyond threshold evaluation.
        """
        
        # Check for conflicting signals
        has_locations = bool(entities.locations)
        has_ages = bool(entities.ages) 
        has_terminology = bool(entities.terminology)
        
        if has_locations and not (has_ages or has_terminology):
            return True, "Location detected without compliance context - unclear intent", "medium"
        
        # Check for uncertain risk assessment
        if llm_result.risk_assessment == "unknown":
            return True, "LLM unable to determine risk level", "medium"
        
        # Check for low entity confidence
        if entities.confidence_scores:
            avg_entity_confidence = sum(entities.confidence_scores.values()) / len(entities.confidence_scores)
            if avg_entity_confidence < 0.7:
                return True, "Low entity detection confidence - may need verification", "medium"
        
        return False, "", "low"
    
    def classify(self, title: str, description: str) -> EnhancedClassificationResult:
        """
        Main classification method implementing the complete feature flow.
        
        This is the primary entry point that orchestrates:
        1. Preprocessing and entity extraction
        2. Entity standardization  
        3. Clear-cut detection (95% cases)
        4. LLM analysis with enhanced prompts
        5. Secondary cross-validation
        6. Confidence calculation
        7. Human intervention determination
        """
        
        start_time = datetime.now()
        
        # Step 1: Preprocessing and entity extraction
        preprocessing_result = self.preprocessor.process(title, description)
        
        # Step 2: Entity standardization
        standardized_entities = self.standardize_entities(preprocessing_result.entities)
        
        # Step 2.5: Process ambiguity in entities
        feature_category = self.determine_feature_category(f"{title} {description}", standardized_entities)
        ambiguity_assessments, disambiguation_result, ambiguity_penalty = self.process_ambiguity(
            preprocessing_result.entities, f"{title} {description}", feature_category
        )
        
        # Step 3: Check for clear-cut cases (95% confidence)
        if preprocessing_result.clear_cut_classification is not None and preprocessing_result.confidence_score >= 0.95:
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return EnhancedClassificationResult(
                needs_geo_logic=preprocessing_result.clear_cut_classification,
                primary_confidence=preprocessing_result.confidence_score,
                secondary_confidence=preprocessing_result.confidence_score,
                overall_confidence=preprocessing_result.confidence_score,
                reasoning=f"Clear-cut detection: High confidence ({preprocessing_result.confidence_score:.3f}) classification based on regex/NER patterns.",
                applicable_regulations=[],
                risk_assessment="medium" if preprocessing_result.clear_cut_classification else "low",
                regulatory_requirements=["Verify specific regulatory requirements"] if preprocessing_result.clear_cut_classification else [],
                evidence_sources=["High-confidence pattern matching", "Entity detection"],
                recommended_actions=["Proceed with compliance implementation"] if preprocessing_result.clear_cut_classification else ["Continue with standard development"],
                standardized_entities=standardized_entities,
                preprocessing_result=preprocessing_result,
                clear_cut_detection=True,
                confidence_breakdown={"clear_cut_confidence": preprocessing_result.confidence_score},
                needs_human_review=False,
                human_review_reason="",
                intervention_priority="low",
                processing_timestamp=datetime.now().isoformat(),
                method_used="clear_cut",
                processing_time_ms=processing_time,
                # Optional fields with defaults
                detailed_confidence=None,
                ambiguity_assessments=ambiguity_assessments,
                disambiguation_result=disambiguation_result,
                ambiguity_confidence_penalty=ambiguity_penalty,
                threshold_decision=None,
                final_action="auto_approve"
            )
        
        # Step 4: Enhanced LLM analysis
        rag_context = self.rag.get_regulatory_context(title, description)
        enhanced_prompt = self.build_enhanced_prompt(title, description, standardized_entities, rag_context)
        
        # Get LLM analysis (this will use the existing llm_classifier with enhanced prompt)
        llm_result = self.llm_classifier.analyze_regulatory_compliance(title, description)
        
        # Step 5: Enhanced secondary cross-validation
        secondary_confidence, secondary_breakdown = self.cross_validate_with_secondary_checks(
            f"{title} {description}", llm_result, standardized_entities
        )
        
        # Step 6: Enhanced confidence calculation using standardized scoring
        detailed_confidence = self.calculate_enhanced_confidence(
            llm_result.confidence, secondary_confidence, standardized_entities, feature_category, secondary_breakdown
        )
        
        # Step 6.5: Apply ambiguity penalty to confidence
        if ambiguity_penalty > 0:
            detailed_confidence = self.apply_ambiguity_penalty(detailed_confidence, ambiguity_penalty)
        
        final_confidence = detailed_confidence.final_confidence
        
        # Convert to legacy format for backward compatibility
        confidence_breakdown = detailed_confidence.confidence_factors
        
        # Step 7: Threshold-based action determination
        threshold_decision, needs_review, review_reason, priority, final_action = self.determine_threshold_based_action(
            final_confidence, feature_category, standardized_entities, llm_result
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return EnhancedClassificationResult(
            needs_geo_logic=llm_result.needs_geo_logic,
            primary_confidence=llm_result.confidence,
            secondary_confidence=secondary_confidence,
            overall_confidence=final_confidence,
            reasoning=llm_result.reasoning,
            applicable_regulations=llm_result.applicable_regulations,
            risk_assessment=llm_result.risk_assessment,
            regulatory_requirements=llm_result.regulatory_requirements,
            evidence_sources=llm_result.evidence_sources,
            recommended_actions=llm_result.recommended_actions,
            standardized_entities=standardized_entities,
            preprocessing_result=preprocessing_result,
            clear_cut_detection=False,
            confidence_breakdown=confidence_breakdown,
            needs_human_review=needs_review,
            human_review_reason=review_reason,
            intervention_priority=priority,
            processing_timestamp=datetime.now().isoformat(),
            method_used="llm_primary" if llm_result.confidence > 0.7 else "llm_secondary",
            processing_time_ms=processing_time,
            # Optional fields with defaults
            detailed_confidence=detailed_confidence,
            ambiguity_assessments=ambiguity_assessments,
            disambiguation_result=disambiguation_result,
            ambiguity_confidence_penalty=ambiguity_penalty,
            threshold_decision=threshold_decision,
            final_action=final_action
        )

# Global enhanced classifier instance
_enhanced_classifier_instance = None

def get_enhanced_classifier() -> EnhancedGeoComplianceClassifier:
    """Get singleton enhanced classifier instance"""
    global _enhanced_classifier_instance
    if _enhanced_classifier_instance is None:
        _enhanced_classifier_instance = EnhancedGeoComplianceClassifier()
    return _enhanced_classifier_instance

if __name__ == "__main__":
    # Test the enhanced classifier
    classifier = EnhancedGeoComplianceClassifier()
    
    # Test cases
    test_cases = [
        ("Utah Minor Curfew", "Implement curfew restrictions for minors in Utah to comply with Utah Social Media Regulation Act"),
        ("A/B Test Feature", "Test new UI design in Canada for user engagement optimization"),
        ("CSAM Detection", "Implement automated child sexual abuse material detection for NCMEC reporting requirements")
    ]
    
    for title, description in test_cases:
        print(f"\n=== Testing: {title} ===")
        result = classifier.classify(title, description)
        print(f"Needs geo-logic: {result.needs_geo_logic}")
        print(f"Overall confidence: {result.overall_confidence:.3f}")
        print(f"Method: {result.method_used}")
        print(f"Needs review: {result.needs_human_review}")
        if result.needs_human_review:
            print(f"Review reason: {result.human_review_reason}")
        print(f"Processing time: {result.processing_time_ms:.1f}ms")
