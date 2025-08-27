import os
import openai
from typing import Dict, List, Optional
import logging
from pydantic import BaseModel
from backend.rag_loader import get_rag_instance

logger = logging.getLogger(__name__)

class LLMClassificationResult(BaseModel):
    needs_geo_logic: bool
    confidence: float
    reasoning: str
    regulations: List[str]
    risk_level: str  # "low", "medium", "high"
    specific_requirements: List[str]

class LLMClassifier:
    """
    LLM-powered classifier for geo-compliance detection using OpenAI GPT-4o-mini
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("No OpenAI API key found. LLM classification will be disabled.")
        
        self.rag = get_rag_instance()
        self.model = "gpt-4o-mini"
        
    def _build_classification_prompt(self, title: str, description: str, rag_context: str) -> str:
        """Build a comprehensive prompt for LLM classification"""
        
        prompt = f"""
You are an expert legal compliance analyst specializing in geographic compliance requirements for software features.

TASK: Analyze the following feature for geo-compliance requirements and determine if it needs geographic-specific logic.

FEATURE TO ANALYZE:
Title: {title}
Description: {description}

RELEVANT REGULATIONS CONTEXT:
{rag_context}

ANALYSIS REQUIREMENTS:
1. Determine if this feature requires geo-specific compliance logic (true/false)
2. Provide confidence level (0.0-1.0)
3. Explain your reasoning in detail
4. List specific regulations that apply
5. Assess risk level (low/medium/high)
6. Identify specific compliance requirements

RESPONSE FORMAT (JSON):
{{
    "needs_geo_logic": true/false,
    "confidence": 0.85,
    "reasoning": "Detailed explanation of why this feature does/doesn't need geo-compliance...",
    "regulations": ["EU DSA", "GDPR", "CA Kids Act"],
    "risk_level": "medium",
    "specific_requirements": [
        "Age verification for users under 18",
        "Data localization for EU users",
        "Content moderation for harmful material"
    ]
}}

IMPORTANT GUIDELINES:
- Be conservative: When in doubt, flag for geo-compliance
- Consider data handling, user age, content moderation, and location services
- Focus on regulations that have geographic scope or jurisdiction-specific requirements
- Provide actionable, specific compliance requirements
- Consider both current and potential future compliance needs

Analyze the feature and respond with the JSON format above:
"""
        return prompt
    
    def classify_feature(self, title: str, description: str) -> LLMClassificationResult:
        """
        Classify a feature using LLM + RAG for geo-compliance requirements
        """
        try:
            # Get RAG context
            rag_context = self.rag.get_context_for_classification(title, description)
            
            # Build prompt
            prompt = self._build_classification_prompt(title, description, rag_context)
            
            # Call OpenAI API
            if not self.api_key:
                logger.warning("No OpenAI API key available, falling back to mock classification")
                return self._mock_classification(title, description)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a legal compliance expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent legal analysis
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle potential markdown formatting)
            if content.startswith("```json"):
                content = content[7:-3]  # Remove ```json and ```
            elif content.startswith("```"):
                content = content[3:-3]  # Remove ``` markers
            
            import json
            result_data = json.loads(content)
            
            return LLMClassificationResult(**result_data)
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            logger.info("Falling back to mock classification")
            return self._mock_classification(title, description)
    
    def _mock_classification(self, title: str, description: str) -> LLMClassificationResult:
        """Fallback mock classification when LLM is unavailable"""
        text = f"{title} {description}".lower()
        
        # Enhanced mock logic
        geo_keywords = ["location", "region", "country", "age", "minor", "child", "personal data", "tracking", "content moderation", "verification"]
        uncertain_keywords = ["user", "profile", "social", "sharing", "recommendation"]
        
        has_geo_keywords = any(keyword in text for keyword in geo_keywords)
        has_uncertain_keywords = any(keyword in text for keyword in uncertain_keywords)
        
        if has_geo_keywords:
            if "age" in text or "minor" in text or "child" in text:
                return LLMClassificationResult(
                    needs_geo_logic=True,
                    confidence=0.9,
                    reasoning="Feature involves age verification or minor protection, requiring geo-specific compliance",
                    regulations=["CA Kids Act", "UT Social Media Act", "FL Minor Protections", "EU DSA"],
                    risk_level="high",
                    specific_requirements=["Age verification system", "Parental consent mechanisms", "Minor data protection"]
                )
            elif "personal data" in text or "tracking" in text:
                return LLMClassificationResult(
                    needs_geo_logic=True,
                    confidence=0.85,
                    reasoning="Feature handles personal data or tracking, subject to regional privacy regulations",
                    regulations=["GDPR", "EU DSA", "CCPA"],
                    risk_level="medium",
                    specific_requirements=["Data localization", "Privacy consent", "Data retention policies"]
                )
            else:
                return LLMClassificationResult(
                    needs_geo_logic=True,
                    confidence=0.7,
                    reasoning="Feature contains geo-sensitive elements requiring regional compliance review",
                    regulations=["EU DSA"],
                    risk_level="medium",
                    specific_requirements=["Regional compliance review", "Local law assessment"]
                )
        elif has_uncertain_keywords:
            return LLMClassificationResult(
                needs_geo_logic=False,
                confidence=0.6,
                reasoning="Feature may have geo-compliance implications but appears low-risk based on current description",
                regulations=[],
                risk_level="low",
                specific_requirements=["Monitor for future compliance needs"]
            )
        else:
            return LLMClassificationResult(
                needs_geo_logic=False,
                confidence=0.8,
                reasoning="Feature appears to be geo-agnostic with no apparent compliance requirements",
                regulations=[],
                risk_level="low",
                specific_requirements=[]
            )

# Global classifier instance
_classifier_instance = None

def get_classifier() -> LLMClassifier:
    """Get singleton classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = LLMClassifier()
    return _classifier_instance
