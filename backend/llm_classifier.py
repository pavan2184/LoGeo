import os
import requests
import json
from typing import Dict, List, Optional
import logging
from pydantic import BaseModel
from backend.rag_loader import get_rag_instance

logger = logging.getLogger(__name__)

class RegulatoryAnalysisResult(BaseModel):
    needs_geo_logic: bool
    confidence: float
    reasoning: str
    applicable_regulations: List[dict]  # [{"name": "GDPR", "jurisdiction": "EU", "relevance": "high", "specific_articles": ["Art. 6", "Art. 17"]}]
    risk_assessment: str  # "low", "medium", "high", "critical"
    regulatory_requirements: List[str]  # Specific legal requirements that must be implemented
    evidence_sources: List[str]  # References to regulation documents and sections used
    recommended_actions: List[str]  # Actionable next steps for compliance team

class RegulatoryComplianceAnalyzer:
    """
    Production-ready regulatory compliance analyzer using FREE Ollama LLM + RAG.
    Uses local Llama 2 model - completely free, no API keys needed!
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.rag = get_rag_instance()
        self.model = "llama2"  # Free Llama 2 model
        
        # Check if Ollama is available
        if self._check_ollama_available():
            self.mode = "llama2"
            logger.info("Regulatory Compliance Analyzer initialized with FREE Llama 2 (Ollama)")
            self._ensure_model_downloaded()
        else:
            self.mode = "rule_based"
            logger.warning("Ollama not available. Running in enhanced rule-based mode with RAG.")
            logger.info("To use FREE LLM: Install Ollama from https://ollama.ai")
        
    def _build_regulatory_analysis_prompt(self, title: str, description: str, rag_context: str) -> str:
        """Build a comprehensive prompt for legitimate regulatory compliance analysis"""
        
        prompt = f"""
You are a senior regulatory compliance expert analyzing software features for geographic-specific legal requirements.

Your task is to provide a thorough, auditable analysis determining whether this feature requires geo-specific compliance logic based on legitimate regulatory sources.

FEATURE ARTIFACT:
Title: {title}
Description: {description}

RELEVANT REGULATORY CONTEXT (from official sources):
{rag_context}

ANALYSIS FRAMEWORK:
You must determine:
1. Does this feature trigger ANY geographic-specific legal requirement?
2. What specific regulations apply and in which jurisdictions?
3. What are the precise legal obligations?
4. What evidence supports this conclusion?

CRITICAL DISTINCTION:
- ✅ Legal requirement: "Feature reads user location to enforce France's copyright rules"
- ✅ Legal requirement: "Requires age gates specific to Indonesia's Child Protection Law"
- ❌ Business decision: "Geofences feature rollout in US for market testing"
- ❓ Unclear intent: "Video filter available globally except KR" (needs human review)

RESPONSE FORMAT (JSON):
{{
    "needs_geo_logic": true/false,
    "confidence": 0.95,
    "reasoning": "Detailed legal analysis with specific regulatory citations...",
    "applicable_regulations": [
        {{
            "name": "EU Digital Services Act",
            "jurisdiction": "European Union", 
            "relevance": "high",
            "specific_articles": ["Article 16", "Article 24"],
            "legal_basis": "Content moderation transparency requirements"
        }}
    ],
    "risk_assessment": "high",
    "regulatory_requirements": [
        "Implement content flagging transparency per EU DSA Article 16",
        "Provide user notification mechanisms as required by Article 24"
    ],
    "evidence_sources": [
        "EU Digital Services Act - Article 16 (Content Moderation)",
        "EU Digital Services Act - Article 24 (Transparency Reports)"
    ],
    "recommended_actions": [
        "Consult legal team for EU DSA compliance implementation",
        "Implement geo-detection for EU users",
        "Design transparent content moderation system"
    ]
}}

REQUIREMENTS:
- Base analysis ONLY on legitimate regulatory sources provided
- Cite specific articles/sections where applicable  
- Distinguish between legal requirements vs business decisions
- Provide audit-ready evidence trail
- Be precise about jurisdictional scope
- Flag unclear cases for human review

Analyze this feature:
"""
        return prompt
    
    def analyze_regulatory_compliance(self, title: str, description: str) -> RegulatoryAnalysisResult:
        """
        Perform comprehensive regulatory compliance analysis using FREE Llama 2 + legitimate sources.
        This is the primary method for production compliance detection.
        """
        try:
            # Get contextual information from legitimate regulatory sources
            rag_context = self.rag.get_regulatory_context(title, description)
            
            if not rag_context or len(rag_context.strip()) < 50:
                logger.warning(f"Insufficient regulatory context found for feature: {title}")
                return self._enhanced_rule_based_analysis(title, description)
            
            if self.mode == "llama2":
                return self._llama2_analysis(title, description, rag_context)
            else:
                return self._enhanced_rule_based_analysis(title, description, rag_context)
            
        except Exception as e:
            logger.error(f"Regulatory analysis failed for feature '{title}': {e}")
            return self._handle_analysis_error(title, description, str(e))
    
    def _llama2_analysis(self, title: str, description: str, rag_context: str) -> RegulatoryAnalysisResult:
        """Use FREE Llama 2 for regulatory analysis"""
        try:
            prompt = self._build_regulatory_analysis_prompt(title, description, rag_context)
            
            # Call Ollama API (completely free!)
            response = requests.post(f"{self.ollama_url}/api/generate", 
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent analysis
                        "num_predict": 2000  # Max tokens
                    }
                },
                timeout=120  # 2 minute timeout for complex analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "").strip()
                
                # Clean JSON formatting
                if content.startswith("```json"):
                    content = content[7:-3]
                elif content.startswith("```"):
                    content = content[3:-3]
                
                result_data = json.loads(content)
                self._validate_analysis_result(result_data)
                
                logger.info(f"FREE Llama 2 analysis completed for feature: {title}")
                return RegulatoryAnalysisResult(**result_data)
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._enhanced_rule_based_analysis(title, description, rag_context)
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from Llama 2: {e}")
            return self._enhanced_rule_based_analysis(title, description, rag_context)
        except Exception as e:
            logger.error(f"Llama 2 analysis failed: {e}")
            return self._enhanced_rule_based_analysis(title, description, rag_context)
    
    def _handle_insufficient_context(self, title: str, description: str) -> RegulatoryAnalysisResult:
        """Handle cases where insufficient regulatory context is available"""
        return RegulatoryAnalysisResult(
            needs_geo_logic=False,  # Conservative: no evidence means no flagging
            confidence=0.3,  # Low confidence due to insufficient data
            reasoning="Insufficient regulatory context found in legitimate sources to determine geo-compliance requirements. Manual review recommended.",
            applicable_regulations=[],
            risk_assessment="unknown",
            regulatory_requirements=["Conduct manual regulatory review"],
            evidence_sources=["No relevant regulatory documents found"],
            recommended_actions=self._generate_contextual_recommendations(
                title, description, [], "unknown", 0.3, False
            )
        )
    
    def _handle_analysis_error(self, title: str, description: str, error_msg: str) -> RegulatoryAnalysisResult:
        """Handle analysis errors with proper audit trail"""
        return RegulatoryAnalysisResult(
            needs_geo_logic=True,  # Conservative: flag for manual review on errors
            confidence=0.0,
            reasoning=f"Regulatory analysis failed: {error_msg}. Manual review required for compliance determination.",
            applicable_regulations=[],
            risk_assessment="critical",
            regulatory_requirements=["Immediate manual legal review required"],
            evidence_sources=[f"Analysis error: {error_msg}"],
            recommended_actions=[
                "Escalate to compliance team immediately",
                "Conduct thorough manual regulatory review", 
                "Do not deploy feature until compliance verified"
            ]
        )
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            response = requests.get(f"{self.ollama_url}/api/version", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _ensure_model_downloaded(self) -> None:
        """Ensure Llama 2 model is downloaded"""
        try:
            # Check if model exists
            response = requests.post(f"{self.ollama_url}/api/show", 
                json={"name": self.model}, timeout=10)
            
            if response.status_code != 200:
                logger.info("Downloading FREE Llama 2 model (first time only)...")
                # This will auto-download the model
                requests.post(f"{self.ollama_url}/api/pull", 
                    json={"name": self.model}, timeout=300)
                logger.info("Llama 2 model ready!")
        except Exception as e:
            logger.warning(f"Could not verify model: {e}")
    
    def _enhanced_rule_based_analysis(self, title: str, description: str, rag_context: str = "") -> RegulatoryAnalysisResult:
        """Enhanced rule-based analysis focused on the 5 key hackathon regulations"""
        text = f"{title} {description}".lower()
        
        # SPECIFIC REGULATION DETECTION - Focused on 5 key laws
        regulation_patterns = {
            "EU_DSA": {
                "keywords": ["eu", "european", "content moderation", "transparency", "risk assessment", "illegal content", "dsa", "digital services"],
                "triggers": ["content flagging", "user reporting", "algorithm transparency", "content removal", "moderation system"],
                "jurisdiction": "European Union",
                "name": "EU Digital Services Act"
            },
            "CA_KIDS_ACT": {
                "keywords": ["california", "age estimation", "privacy by default", "minor", "child", "data minimization", "best interests"],
                "triggers": ["age verification", "privacy settings", "data collection", "personalization", "targeted advertising"],
                "jurisdiction": "California",
                "name": "California Age-Appropriate Design Code Act"
            },
            "FL_MINOR_PROTECTIONS": {
                "keywords": ["florida", "parental consent", "minor account", "age verification", "harmful content", "social media addiction"],
                "triggers": ["parental notification", "account restrictions", "time limits", "content filtering"],
                "jurisdiction": "Florida", 
                "name": "Florida Online Protections for Minors"
            },
            "UT_SOCIAL_MEDIA": {
                "keywords": ["utah", "curfew", "time restrictions", "parental access", "minor verification", "social media regulation"],
                "triggers": ["10:30 pm", "6:30 am", "account lockout", "parental controls", "identity verification"],
                "jurisdiction": "Utah",
                "name": "Utah Social Media Regulation Act"  
            },
            "US_NCMEC": {
                "keywords": ["child sexual abuse", "ncmec", "csam", "reporting", "abuse content", "child exploitation"],
                "triggers": ["content scanning", "abuse detection", "automated reporting", "law enforcement"],
                "jurisdiction": "United States",
                "name": "US NCMEC Reporting Requirements"
            }
        }
        
        # Business decision keywords (should NOT flag)
        business_keywords = ["market testing", "a/b test", "user engagement", "revenue optimization", "conversion", "retention", "growth"]
        
        # Geographic testing keywords (might be business, not legal)
        ambiguous_keywords = ["rollout", "launch", "pilot", "experiment", "beta", "test market"]
        
        # STEP 1: Check if it's clearly a business decision (should NOT flag)
        if any(keyword in text for keyword in business_keywords) and not any(
            any(trigger in text for trigger in reg["triggers"]) 
            for reg in regulation_patterns.values()
        ):
            return RegulatoryAnalysisResult(
                needs_geo_logic=False,
                confidence=0.90,
                reasoning="Feature appears to be a business decision for market testing/optimization rather than a legal compliance requirement.",
                applicable_regulations=[],
                risk_assessment="low",
                regulatory_requirements=[],
                evidence_sources=["Business pattern detection"],
                recommended_actions=self._generate_contextual_recommendations(
                    title, description, [], "low", 0.90, False
                )
            )
        
        # STEP 2: Detect specific regulations
        detected_regulations = []
        regulation_scores = {}
        
        for reg_id, reg_data in regulation_patterns.items():
            keyword_score = sum(1 for keyword in reg_data["keywords"] if keyword in text)
            trigger_score = sum(2 for trigger in reg_data["triggers"] if trigger in text)  # Triggers worth more
            total_score = keyword_score + trigger_score
            
            if total_score > 0:
                regulation_scores[reg_id] = total_score
                detected_regulations.append({
                    "name": reg_data["name"],
                    "jurisdiction": reg_data["jurisdiction"],
                    "relevance": "high" if total_score >= 3 else "medium",
                    "specific_articles": [],
                    "legal_basis": f"Detected {keyword_score} keywords + {trigger_score//2} triggers"
                })
        
        # STEP 3: Analyze results
        if detected_regulations:
            max_score = max(regulation_scores.values())
            confidence = min(0.95, 0.60 + (max_score * 0.1))  # Scale confidence with detection strength
            
            if max_score >= 3:  # Strong detection
                return RegulatoryAnalysisResult(
                    needs_geo_logic=True,
                    confidence=confidence,
                    reasoning=f"Strong regulatory compliance signals detected. Feature triggers: {', '.join([reg['name'] for reg in detected_regulations])}. Geographic-specific implementation required.",
                    applicable_regulations=detected_regulations,
                    risk_assessment="high",
                    regulatory_requirements=[
                        "Implement jurisdiction-specific compliance logic",
                        "Configure geographic detection system",
                        "Establish regulatory audit trail",
                        "Design compliance-appropriate user experience"
                    ],
                    evidence_sources=[f"Regulation detection: {', '.join(regulation_scores.keys())}", "Legitimate regulatory document analysis"],
                    recommended_actions=self._generate_contextual_recommendations(
                        title, description, detected_regulations, "high", confidence, True
                    )
                )
            else:  # Weak detection - might be compliance related
                return RegulatoryAnalysisResult(
                    needs_geo_logic=True,
                    confidence=confidence,
                    reasoning=f"Potential regulatory compliance requirements detected: {', '.join([reg['name'] for reg in detected_regulations])}. Manual legal review recommended.",
                    applicable_regulations=detected_regulations,
                    risk_assessment="medium",
                    regulatory_requirements=["Legal review required to determine specific obligations"],
                    evidence_sources=[f"Weak regulation detection: {', '.join(regulation_scores.keys())}"],
                    recommended_actions=self._generate_contextual_recommendations(
                        title, description, detected_regulations, "medium", confidence, True
                    )
                )
        
        # STEP 4: Check for ambiguous cases
        if any(keyword in text for keyword in ambiguous_keywords):
            return RegulatoryAnalysisResult(
                needs_geo_logic=False,  # Conservative - assume business unless clear legal trigger
                confidence=0.50,  # Low confidence - needs human review
                reasoning="Feature contains geographic elements but unclear if driven by legal requirements or business decisions. Manual review recommended to determine intent.",
                applicable_regulations=[],
                risk_assessment="unknown", 
                regulatory_requirements=["Manual review to determine business vs legal requirements"],
                evidence_sources=["Ambiguous geographic pattern detection"],
                recommended_actions=self._generate_contextual_recommendations(
                    title, description, [], "unknown", 0.50, False
                )
            )
        
        # STEP 5: No regulatory indicators found
        return RegulatoryAnalysisResult(
            needs_geo_logic=False,
            confidence=0.85,
            reasoning="No clear indicators of the 5 key regulatory requirements (EU DSA, CA Kids Act, FL Minor Protections, UT Social Media Act, US NCMEC) detected. Feature appears to be standard functionality.",
            applicable_regulations=[],
            risk_assessment="low",
            regulatory_requirements=[],
            evidence_sources=["5-regulation focused analysis"],
            recommended_actions=self._generate_contextual_recommendations(
                title, description, [], "low", 0.85, False
            )
        )
    
    def _generate_contextual_recommendations(self, 
                                           title: str, 
                                           description: str, 
                                           detected_regulations: List[dict], 
                                           risk_assessment: str,
                                           confidence: float,
                                           needs_geo_logic: bool) -> List[str]:
        """Generate specific, contextual recommendations based on analysis results"""
        
        recommendations = []
        text = f"{title} {description}".lower()
        
        # High-risk legal compliance actions
        if risk_assessment == "high" and needs_geo_logic:
            if any("gdpr" in reg.get("name", "").lower() for reg in detected_regulations):
                recommendations.extend([
                    "Implement GDPR Article 8 compliant age verification for EU users",
                    "Set up EU-specific data processing consent mechanisms",
                    "Create GDPR-compliant data retention and deletion processes"
                ])
            
            if any("coppa" in reg.get("name", "").lower() for reg in detected_regulations):
                recommendations.extend([
                    "Implement COPPA-compliant parental consent workflow for users under 13",
                    "Set up US-specific age verification and data minimization",
                    "Create COPPA-compliant data deletion processes"
                ])
            
            if any("california" in reg.get("jurisdiction", "").lower() for reg in detected_regulations):
                recommendations.extend([
                    "Implement California Age-Appropriate Design Code compliance",
                    "Set up California-specific privacy settings for minors",
                    "Create opt-out mechanisms for California teens"
                ])
            
            if any("utah" in reg.get("jurisdiction", "").lower() for reg in detected_regulations):
                recommendations.extend([
                    "Implement Utah Social Media Act curfew restrictions",
                    "Set up time-based access controls for Utah minors",
                    "Create parental notification system for Utah users"
                ])
            
            if any("florida" in reg.get("jurisdiction", "").lower() for reg in detected_regulations):
                recommendations.extend([
                    "Implement Florida Online Protections for Minors compliance",
                    "Set up enhanced parental controls for Florida minors",
                    "Create Florida-specific content filtering mechanisms"
                ])
            
            if any("ncmec" in reg.get("name", "").lower() for reg in detected_regulations):
                recommendations.extend([
                    "Implement NCMEC CyberTipline reporting integration",
                    "Set up automated CSAM detection and reporting",
                    "Create mandatory reporter training for content moderation team"
                ])
        
        # Medium-risk actions
        elif risk_assessment == "medium":
            if confidence < 0.7:
                recommendations.extend([
                    f"Conduct targeted legal review focusing on {', '.join([reg.get('jurisdiction', 'Unknown') for reg in detected_regulations])}",
                    "Validate regulatory applicability with compliance team",
                    "Document business justification if no compliance requirements found"
                ])
            else:
                recommendations.extend([
                    "Implement basic geo-detection for regulatory compliance",
                    "Set up monitoring for compliance-related user actions",
                    "Create documentation for audit trail"
                ])
        
        # Feature-specific recommendations based on content
        if "age" in text and "verification" in text:
            recommendations.append("Implement secure age verification using government-issued ID or credit card verification")
        
        if "parental" in text or "parent" in text:
            recommendations.append("Design COPPA-compliant parental consent flow with email verification")
        
        if "content" in text and "moderation" in text:
            recommendations.append("Implement jurisdiction-specific content moderation policies")
        
        if "data" in text and ("storage" in text or "processing" in text):
            recommendations.append("Review data localization requirements for applicable jurisdictions")
        
        if "analytics" in text or "tracking" in text:
            recommendations.append("Implement privacy-compliant analytics with jurisdiction-specific consent")
        
        # Low-risk or business features
        if risk_assessment == "low" or not needs_geo_logic:
            if "test" in text or "experiment" in text:
                recommendations.extend([
                    "Proceed with A/B testing following standard privacy practices",
                    "Ensure test data collection complies with applicable privacy laws",
                    "Document test parameters for compliance review if needed"
                ])
            elif "performance" in text or "optimization" in text:
                recommendations.extend([
                    "Proceed with performance improvements following standard security review",
                    "Ensure optimization doesn't impact compliance-related functionality",
                    "Monitor performance impact on geo-compliance features"
                ])
            else:
                recommendations.extend([
                    "Proceed with standard development and security review processes",
                    "Monitor for any compliance impacts during development",
                    "Include privacy-by-design principles in implementation"
                ])
        
        # Add general geo-logic recommendations if needed
        if needs_geo_logic and not any("geo" in rec.lower() for rec in recommendations):
            recommendations.extend([
                "Implement accurate geo-location detection using IP geolocation and GPS",
                "Set up jurisdiction-specific feature flags and configuration",
                "Create monitoring dashboard for geo-compliance effectiveness"
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        # Limit to most relevant recommendations (max 6)
        return unique_recommendations[:6] if len(unique_recommendations) > 6 else unique_recommendations

    def _validate_analysis_result(self, result_data: dict) -> None:
        """Validate that LLM response contains required fields"""
        required_fields = [
            "needs_geo_logic", "confidence", "reasoning", "applicable_regulations",
            "risk_assessment", "regulatory_requirements", "evidence_sources", "recommended_actions"
        ]
        
        missing_fields = [field for field in required_fields if field not in result_data]
        if missing_fields:
            raise ValueError(f"LLM response missing required fields: {missing_fields}")

# Global analyzer instance
_analyzer_instance = None

def get_classifier() -> RegulatoryComplianceAnalyzer:
    """Get singleton regulatory compliance analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = RegulatoryComplianceAnalyzer()
    return _analyzer_instance
