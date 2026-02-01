#!/usr/bin/env python3
"""
Simple Backend Server - Integrated System Without Heavy Dependencies

This provides a basic FastAPI server for testing the frontend with the integrated
single feature analysis + enhanced threshold system without requiring pandas,
faiss, etc.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Geo-Compliance API", version="1.0.0")

# Request/Response models
class ClassificationRequest(BaseModel):
    title: str
    description: str

class ClassificationResponse(BaseModel):
    needs_geo_logic: bool
    primary_confidence: float
    secondary_confidence: float
    overall_confidence: float
    reasoning: str
    applicable_regulations: list
    risk_assessment: str
    regulatory_requirements: list
    evidence_sources: list
    recommended_actions: list
    standardized_entities: dict
    preprocessing_result: dict
    clear_cut_detection: bool
    confidence_breakdown: dict
    needs_human_review: bool
    human_review_reason: str
    intervention_priority: str
    processing_timestamp: str
    method_used: str
    processing_time_ms: float
    # Enhanced threshold system fields
    categories_detected: Optional[list] = None
    applicable_threshold: Optional[float] = None
    threshold_violations: Optional[list] = None
    escalation_rule: Optional[str] = None
    escalation_reason: Optional[str] = None

# Initialize classifier
try:
    from backend.enhanced_classifier import get_enhanced_classifier
    classifier = get_enhanced_classifier()
    logger.info("✅ Integrated classifier initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize classifier: {e}")
    classifier = None

@app.get("/")
async def root():
    return {
        "message": "Simple Geo-Compliance API", 
        "status": "running",
        "integrated_system": "single_feature_analysis + enhanced_threshold_system",
        "fallback_mode": "faiss_not_required"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "classifier_loaded": classifier is not None,
        "integrated_system": True
    }

@app.post("/classify_enhanced", response_model=ClassificationResponse)
async def classify_enhanced(request: ClassificationRequest):
    """Enhanced classification with integrated threshold system"""
    
    if classifier is None:
        raise HTTPException(status_code=500, detail="Classifier not initialized")
    
    try:
        logger.info(f"Classifying: {request.title}")
        
        # Use the integrated classifier
        result = classifier.classify(request.title, request.description)
        
        # Convert result to response format
        response = ClassificationResponse(
            needs_geo_logic=result.needs_geo_logic,
            primary_confidence=result.primary_confidence,
            secondary_confidence=result.secondary_confidence,
            overall_confidence=result.overall_confidence,
            reasoning=result.reasoning,
            applicable_regulations=result.applicable_regulations,
            risk_assessment=result.risk_assessment,
            regulatory_requirements=result.regulatory_requirements,
            evidence_sources=result.evidence_sources,
            recommended_actions=result.recommended_actions,
            standardized_entities={
                "locations": result.standardized_entities.locations,
                "ages": result.standardized_entities.ages,
                "terminology": result.standardized_entities.terminology,
                "confidence_scores": result.standardized_entities.confidence_scores
            },
            preprocessing_result={
                "original_text": getattr(result.preprocessing_result, 'original_text', ''),
                "cleaned_text": getattr(result.preprocessing_result, 'cleaned_text', ''),
                "confidence_score": getattr(result.preprocessing_result, 'confidence_score', 0.0)
            },
            clear_cut_detection=result.clear_cut_detection,
            confidence_breakdown=result.confidence_breakdown,
            needs_human_review=result.needs_human_review,
            human_review_reason=result.human_review_reason,
            intervention_priority=result.intervention_priority,
            processing_timestamp=result.processing_timestamp,
            method_used=result.method_used,
            processing_time_ms=result.processing_time_ms,
            # Enhanced threshold system fields
            categories_detected=result.categories_detected,
            applicable_threshold=result.applicable_threshold,
            threshold_violations=result.threshold_violations,
            escalation_rule=result.escalation_rule.value if result.escalation_rule else None,
            escalation_reason=result.escalation_reason
        )
        
        logger.info(f"✅ Classification completed - Confidence: {result.overall_confidence:.3f}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Classification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Backend Server...")
    print("📊 Integrated System: Single Feature Analysis + Enhanced Threshold System")
    print("🔧 Fallback Mode: Working without heavy dependencies")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📋 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
