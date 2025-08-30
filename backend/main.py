from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
import csv
import io
from typing import List, Union, Dict, Any, Optional
import json
from datetime import datetime
import os
import logging
from dataclasses import asdict
from backend.llm_classifier import get_classifier, RegulatoryAnalysisResult
from backend.rag_loader import get_rag_instance
from backend.geo_compliance import get_geo_engine
from backend.supabase_client import get_supabase_client
from backend.enhanced_classifier import get_enhanced_classifier, EnhancedClassificationResult
from backend.feedback_system import get_feedback_processor, FeedbackType, InterventionPriority

app = FastAPI(title="Geo-Compliance Detection API", version="1.0.0")

# Setup logger
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class FeatureArtifact(BaseModel):
    title: str
    description: str

class ComplianceResult(BaseModel):
    needs_geo_logic: bool
    confidence: float
    reasoning: str
    applicable_regulations: List[dict]  # [{"name": "GDPR", "jurisdiction": "EU", "relevance": "high"}]
    risk_assessment: str  # "low", "medium", "high", "critical"
    regulatory_requirements: List[str]
    evidence_sources: List[str]  # References to regulation documents used
    recommended_actions: List[str]  # What compliance team should do next

class EnhancedComplianceResult(BaseModel):
    # Core classification
    needs_geo_logic: bool
    primary_confidence: float
    secondary_confidence: float
    overall_confidence: float
    
    # Detailed analysis
    reasoning: str
    applicable_regulations: List[dict]
    risk_assessment: str
    regulatory_requirements: List[str]
    evidence_sources: List[str]
    recommended_actions: List[str]
    
    # Enhanced features
    standardized_entities: dict
    clear_cut_detection: bool
    confidence_breakdown: dict
    
    # Human intervention
    needs_human_review: bool
    human_review_reason: str
    intervention_priority: str
    
    # Processing info
    method_used: str
    processing_time_ms: float

class BatchResult(BaseModel):
    total_processed: int
    results: List[dict]

# New geo-compliance models
class AccessRequest(BaseModel):
    user_id: str
    feature_name: str
    country: str

class AccessResponse(BaseModel):
    access_granted: bool
    reason: str

class BatchAccessRequest(BaseModel):
    requests: List[Dict[str, str]]

class BatchAccessResponse(BaseModel):
    results: List[Dict[str, Any]]

def classify_feature_enhanced(title: str, description: str) -> EnhancedComplianceResult:
    """
    Enhanced feature classification using the complete multi-stage pipeline.
    Implements the full feature flow with preprocessing, NER, standardization, 
    confidence calculation, and human intervention alerts.
    """
    enhanced_classifier = get_enhanced_classifier()
    feedback_processor = get_feedback_processor()
    
    # Get comprehensive analysis
    result = enhanced_classifier.classify(title, description)
    
    # Create intervention alert if needed
    if result.needs_human_review:
        priority_map = {
            "low": InterventionPriority.LOW,
            "medium": InterventionPriority.MEDIUM, 
            "high": InterventionPriority.HIGH,
            "critical": InterventionPriority.CRITICAL
        }
        
        alert_id = feedback_processor.create_intervention_alert(
            title,
            description,
            asdict(result),
            result.human_review_reason,
            priority_map.get(result.intervention_priority, InterventionPriority.MEDIUM)
        )
        
        logger.info(f"Human intervention alert created: {alert_id} for feature: {title}")
    
    # Convert to API response model
    return EnhancedComplianceResult(
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
        standardized_entities=asdict(result.standardized_entities),
        clear_cut_detection=result.clear_cut_detection,
        confidence_breakdown=result.confidence_breakdown,
        needs_human_review=result.needs_human_review,
        human_review_reason=result.human_review_reason,
        intervention_priority=result.intervention_priority,
        method_used=result.method_used,
        processing_time_ms=result.processing_time_ms
    )

def classify_feature(title: str, description: str) -> ComplianceResult:
    """
    Analyze feature artifacts to determine if geo-specific compliance logic is required.
    Uses LLM + RAG with legitimate regulatory sources for auditable compliance detection.
    """
    classifier = get_classifier()
    
    # Get comprehensive regulatory analysis from LLM + RAG
    analysis_result = classifier.analyze_regulatory_compliance(title, description)
    
    return ComplianceResult(
        needs_geo_logic=analysis_result.needs_geo_logic,
        confidence=analysis_result.confidence,
        reasoning=analysis_result.reasoning,
        applicable_regulations=analysis_result.applicable_regulations,
        risk_assessment=analysis_result.risk_assessment,
        regulatory_requirements=analysis_result.regulatory_requirements,
        evidence_sources=analysis_result.evidence_sources,
        recommended_actions=analysis_result.recommended_actions
    )

async def log_result(title: str, description: str, result: ComplianceResult):
    """Log regulatory compliance analysis results for audit trail"""
    try:
        supabase_client = get_supabase_client()
        
        # Try to log to Supabase first
        if supabase_client.is_connected():
            await supabase_client.log_compliance_analysis(
                title=title,
                description=description,
                needs_geo_logic=result.needs_geo_logic,
                confidence=result.confidence,
                reasoning=result.reasoning,
                applicable_regulations=result.applicable_regulations,
                risk_assessment=result.risk_assessment,
                regulatory_requirements=result.regulatory_requirements,
                evidence_sources=result.evidence_sources,
                recommended_actions=result.recommended_actions
            )
        else:
            # Fallback to CSV for audit purposes
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "description": description,
                "needs_geo_logic": result.needs_geo_logic,
                "confidence": result.confidence,
                "reasoning": result.reasoning,
                "applicable_regulations": json.dumps(result.applicable_regulations),
                "risk_assessment": result.risk_assessment,
                "regulatory_requirements": "; ".join(result.regulatory_requirements),
                "evidence_sources": "; ".join(result.evidence_sources),
                "recommended_actions": "; ".join(result.recommended_actions)
            }
            
            # Ensure results directory exists
            os.makedirs("results", exist_ok=True)
            
            # Append to results.csv
            file_exists = os.path.exists("results/results.csv")
            with open("results/results.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=log_entry.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(log_entry)
            
    except Exception as e:
        print(f"Warning: Failed to log result: {e}")
        # Continue execution even if logging fails

@app.get("/")
async def root():
    return {"message": "Geo-Compliance Detection API", "version": "1.0.0"}



@app.post("/classify", response_model=ComplianceResult)
async def classify_single_feature(
    feature: FeatureArtifact
):
    """
    Classify a single feature artifact for geo-compliance requirements.
    
    Returns:
    - needs_geo_logic: true/false/"uncertain"
    - reasoning: explanation for the classification
    - regulations: list of relevant regulations
    """
    try:
        result = classify_feature(feature.title, feature.description)
        
        # Log result for audit trail
        await log_result(feature.title, feature.description, result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/classify_enhanced", response_model=EnhancedComplianceResult)
async def classify_single_feature_enhanced(
    feature: FeatureArtifact
):
    """
    Enhanced classification with complete multi-stage pipeline.
    
    Implements the full feature flow including:
    - Preprocessing and tokenization
    - NER and regex detection for clear-cut cases
    - Entity standardization using glossary
    - Multi-stage classification with confidence scoring
    - Human intervention alerts for low confidence cases
    
    Returns comprehensive analysis with confidence breakdown.
    """
    try:
        result = classify_feature_enhanced(feature.title, feature.description)
        
        # Log enhanced result for audit trail (convert to legacy format for compatibility)
        legacy_result = ComplianceResult(
            needs_geo_logic=result.needs_geo_logic,
            confidence=result.overall_confidence,
            reasoning=result.reasoning,
            applicable_regulations=result.applicable_regulations,
            risk_assessment=result.risk_assessment,
            regulatory_requirements=result.regulatory_requirements,
            evidence_sources=result.evidence_sources,
            recommended_actions=result.recommended_actions
        )
        await log_result(feature.title, feature.description, legacy_result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced classification failed: {str(e)}")

@app.post("/batch_classify")
async def batch_classify_features(
    file: UploadFile = File(...)
):
    """
    Upload a CSV file with feature artifacts and return classifications.
    
    Expected CSV format:
    title,description
    "Feature Name","Feature description text"
    
    Returns: CSV file with original data + classification results
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read uploaded CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns (accept multiple naming conventions)
        title_col = None
        desc_col = None
        
        # Check for title column variants
        for col in ['title', 'feature_name', 'name']:
            if col in df.columns:
                title_col = col
                break
                
        # Check for description column variants  
        for col in ['description', 'feature_description', 'desc']:
            if col in df.columns:
                desc_col = col
                break
        
        if title_col is None or desc_col is None:
            missing = []
            if title_col is None:
                missing.append("title/feature_name/name")
            if desc_col is None:
                missing.append("description/feature_description/desc")
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain columns: {', '.join(missing)}"
            )
        
        # Process each row
        results = []
        for _, row in df.iterrows():
            title = str(row[title_col]) if pd.notna(row[title_col]) else ""
            description = str(row[desc_col]) if pd.notna(row[desc_col]) else ""
            
            # Classify the feature (use enhanced classifier)
            enhanced_classification = classify_feature_enhanced(title, description)
            
            # Convert to legacy format for batch processing compatibility
            classification = ComplianceResult(
                needs_geo_logic=enhanced_classification.needs_geo_logic,
                confidence=enhanced_classification.overall_confidence,
                reasoning=enhanced_classification.reasoning,
                applicable_regulations=enhanced_classification.applicable_regulations,
                risk_assessment=enhanced_classification.risk_assessment,
                regulatory_requirements=enhanced_classification.regulatory_requirements,
                evidence_sources=enhanced_classification.evidence_sources,
                recommended_actions=enhanced_classification.recommended_actions
            )
            
            # Log result
            await log_result(title, description, classification)
            
            # Add regulatory compliance analysis to row
            result_row = row.to_dict()
            result_row.update({
                'needs_geo_logic': classification.needs_geo_logic,
                'confidence': classification.confidence,
                'reasoning': classification.reasoning,
                'applicable_regulations': json.dumps(classification.applicable_regulations),
                'risk_assessment': classification.risk_assessment,
                'regulatory_requirements': "; ".join(classification.regulatory_requirements),
                'evidence_sources': "; ".join(classification.evidence_sources),
                'recommended_actions': "; ".join(classification.recommended_actions),
                'analyzed_at': datetime.now().isoformat()
            })
            results.append(result_row)
        
        # Create output CSV
        output_df = pd.DataFrame(results)
        output_csv = io.StringIO()
        output_df.to_csv(output_csv, index=False)
        output_csv.seek(0)
        
        # Return CSV as downloadable file
        response = StreamingResponse(
            io.BytesIO(output_csv.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=classified_features.csv"}
        )
        
        return response
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ===== GEO-COMPLIANCE ENDPOINTS =====

@app.post("/check_access", response_model=AccessResponse)
async def check_access(request: AccessRequest):
    """
    Check if access should be granted based on geo-compliance rules.
    
    Request body:
    {
        "user_id": "string",
        "feature_name": "string", 
        "country": "string"
    }
    
    Returns:
    {
        "access_granted": true|false,
        "reason": "explanation for the decision"
    }
    """
    try:
        geo_engine = get_geo_engine()
        access_granted, reason = await geo_engine.check_access(
            request.user_id, 
            request.feature_name, 
            request.country
        )
        
        return AccessResponse(
            access_granted=access_granted,
            reason=reason
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error checking access: {str(e)}"
        )

@app.get("/logs")
async def get_access_logs(limit: int = 100):
    """
    Retrieve access logs from the database.
    
    Query parameters:
    - limit: Maximum number of logs to retrieve (default: 100)
    
    Returns:
    List of access log entries with user_id, feature_name, country, 
    access_granted, and timestamp.
    """
    try:
        supabase_client = get_supabase_client()
        logs = await supabase_client.get_access_logs(limit)
        
        return {
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving logs: {str(e)}"
        )

@app.post("/batch_check", response_model=BatchAccessResponse) 
async def batch_check_access(
    file: UploadFile = File(...)
):
    """
    Upload a CSV file with access requests and return results.
    
    Expected CSV format:
    user_id,feature_name,country
    "user123","user_registration","US"
    "user456","age_verification","EU"
    
    Returns: JSON with access results for each request
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read uploaded CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_cols = ['user_id', 'feature_name', 'country']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain columns: {', '.join(required_cols)}"
            )
        
        # Process each row
        geo_engine = get_geo_engine()
        requests = []
        
        for _, row in df.iterrows():
            requests.append({
                "user_id": str(row['user_id']) if pd.notna(row['user_id']) else "",
                "feature_name": str(row['feature_name']) if pd.notna(row['feature_name']) else "",
                "country": str(row['country']) if pd.notna(row['country']) else ""
            })
        
        results = await geo_engine.batch_check_access(requests)
        
        return BatchAccessResponse(results=results)
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.get("/regulations")
async def list_regulations():
    """List all available regulations"""
    try:
        rag = get_rag_instance()
        regulations = rag.load_regulations()
        return {
            "regulations": [reg['name'] for reg in regulations],
            "count": len(regulations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load regulations: {str(e)}")

@app.post("/search_regulations")
async def search_regulations(query: str):
    """Search regulations for relevant content"""
    try:
        rag = get_rag_instance()
        results = rag.search(query, k=5)
        return {
            "query": query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/compliance_audit")
async def get_compliance_audit(limit: int = 50):
    """
    Retrieve regulatory compliance analysis results for audit purposes.
    
    Query parameters:
    - limit: Maximum number of results to retrieve (default: 50)
    
    Returns:
    List of compliance analysis results with full audit trail
    """
    try:
        supabase_client = get_supabase_client()
        
        if supabase_client.is_connected():
            results = await supabase_client.get_compliance_audit(limit)
            return {
                "audit_records": results,
                "count": len(results),
                "timestamp": datetime.now().isoformat(),
                "audit_trail": True
            }
        else:
            # Fallback to CSV audit records
            results_file = "results/results.csv"
            if os.path.exists(results_file):
                df = pd.read_csv(results_file)
                records = df.to_dict('records')[-limit:]  # Get latest records
                return {
                    "audit_records": records,
                    "count": len(records),
                    "timestamp": datetime.now().isoformat(),
                    "audit_trail": True,
                    "source": "CSV fallback"
                }
            else:
                return {
                    "audit_records": [],
                    "count": 0,
                    "timestamp": datetime.now().isoformat(),
                    "note": "No audit records available"
                }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving compliance audit records: {str(e)}"
        )

@app.get("/geo_rules/{feature_name}")
async def get_geo_rules(feature_name: str):
    """Get geo-compliance rules for a specific feature"""
    try:
        geo_engine = get_geo_engine()
        geo_rules = getattr(geo_engine, 'rules', {})
        
        if feature_name in geo_rules:
            rule = geo_rules[feature_name]
            return {
                "feature_name": feature_name,
                "allowed_countries": rule.get("allowed_countries", []),
                "blocked_countries": rule.get("blocked_countries", []),
                "compliance_note": rule.get("compliance_note", ""),
                "rule_exists": True
            }
        else:
            return {
                "feature_name": feature_name,
                "allowed_countries": [],
                "blocked_countries": [],
                "compliance_note": "No specific geo-compliance rules configured",
                "rule_exists": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get geo rules: {str(e)}")

@app.get("/all_geo_rules")
async def get_all_geo_rules():
    """Get all available geo-compliance rules"""
    try:
        geo_engine = get_geo_engine()
        geo_rules = getattr(geo_engine, 'rules', {})
        
        rules_list = []
        for feature_name, rule in geo_rules.items():
            rules_list.append({
                "feature_name": feature_name,
                "allowed_countries": rule.get("allowed_countries", []),
                "blocked_countries": rule.get("blocked_countries", []),
                "compliance_note": rule.get("compliance_note", "")
            })
        
        return {
            "total_rules": len(rules_list),
            "rules": rules_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get all geo rules: {str(e)}")

@app.get("/stats")
async def get_statistics():
    """Get classification statistics from Supabase"""
    try:
        supabase_client = get_supabase_client()
        
        # Try to get statistics from Supabase first
        if supabase_client.is_connected():
            stats = await supabase_client.get_classification_statistics()
            return stats
        else:
            # Fallback to CSV if Supabase is not available
            results_file = "results/results.csv"
            if not os.path.exists(results_file):
                return {
                    "total_classifications": 0,
                    "compliance_required": 0,
                    "no_compliance_needed": 0,
                    "average_confidence": 0.0,
                    "risk_levels": {"low": 0, "medium": 0, "high": 0}
                }
            
            df = pd.read_csv(results_file)
            
            total = len(df)
            compliance_required = len(df[df['needs_geo_logic'] == True])
            no_compliance_needed = len(df[df['needs_geo_logic'] == False])
            avg_confidence = df['confidence'].mean() if 'confidence' in df.columns else 0.0
            
            risk_levels = {"low": 0, "medium": 0, "high": 0}
            if 'risk_level' in df.columns:
                risk_counts = df['risk_level'].value_counts()
                for level in risk_levels:
                    risk_levels[level] = int(risk_counts.get(level, 0))
            
            return {
                "total_classifications": total,
                "compliance_required": compliance_required,
                "no_compliance_needed": no_compliance_needed,
                "average_confidence": round(avg_confidence, 3),
                "risk_levels": risk_levels
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/regulatory_coverage")
async def get_regulatory_coverage():
    """Get coverage analysis of loaded regulatory documents"""
    try:
        rag = get_rag_instance()
        regulations = rag.load_regulations()
        
        coverage_info = {
            "total_regulations": len(regulations),
            "regulations": [
                {
                    "name": reg["name"],
                    "filename": reg.get("filename", ""),
                    "content_length": len(reg["content"]),
                    "jurisdiction": reg.get("jurisdiction", "Unknown"),
                    "last_updated": reg.get("last_updated", "Unknown")
                }
                for reg in regulations
            ],
            "jurisdictions_covered": list(set(
                reg.get("jurisdiction", "Unknown") for reg in regulations
            )),
            "system_status": "operational"
        }
        
        return coverage_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get regulatory coverage: {str(e)}")

# ===== HUMAN INTERVENTION AND FEEDBACK ENDPOINTS =====

class FeedbackSubmission(BaseModel):
    reviewer_id: str
    feedback_type: str  # "classification_correction", "entity_correction", etc.
    original_classification: dict
    corrections: dict
    reasoning: str
    additional_notes: str = ""

class ThresholdRuleUpdate(BaseModel):
    confidence_threshold: float
    escalation_rule: str  # "human_review", "auto_ok", "ignore"
    description: str
    categories: List[str]
    priority: str  # "high", "medium", "low"
    below_threshold_action: str  # "human", "auto_ok", "ignore"

@app.get("/alerts")
async def get_intervention_alerts(priority: Optional[str] = None):
    """Get pending human intervention alerts"""
    try:
        feedback_processor = get_feedback_processor()
        pending_alerts = feedback_processor.get_pending_alerts(priority)
        
        return {
            "alerts": [asdict(alert) for alert in pending_alerts],
            "count": len(pending_alerts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackSubmission):
    """Submit human feedback for system improvement"""
    try:
        feedback_processor = get_feedback_processor()
        
        # Map string to enum
        feedback_type_map = {
            "classification_correction": FeedbackType.CLASSIFICATION_CORRECTION,
            "entity_correction": FeedbackType.ENTITY_CORRECTION,
            "confidence_adjustment": FeedbackType.CONFIDENCE_ADJUSTMENT,
            "new_pattern": FeedbackType.NEW_PATTERN,
            "regulatory_update": FeedbackType.REGULATORY_UPDATE
        }
        
        feedback_type_enum = feedback_type_map.get(feedback.feedback_type, FeedbackType.CLASSIFICATION_CORRECTION)
        
        feedback_id = feedback_processor.submit_feedback(
            feedback_type_enum,
            feedback.reviewer_id,
            feedback.original_classification,
            feedback.corrections,
            feedback.reasoning,
            feedback.additional_notes
        )
        
        return {
            "feedback_id": feedback_id,
            "status": "submitted",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolution: dict):
    """Resolve a human intervention alert"""
    try:
        feedback_processor = get_feedback_processor()
        
        feedback_processor.resolve_alert(
            alert_id,
            resolution.get("reviewer_id", "unknown"),
            resolution.get("notes", "")
        )
        
        return {
            "alert_id": alert_id,
            "status": "resolved",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@app.get("/performance")
async def get_performance_metrics(days: int = 30):
    """Get system performance metrics and trends"""
    try:
        feedback_processor = get_feedback_processor()
        performance_summary = feedback_processor.get_performance_summary(days)
        
        return performance_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@app.get("/glossary/locations")
async def get_location_glossary():
    """Get all location mappings from the glossary"""
    try:
        from backend.glossary import get_glossary
        glossary = get_glossary()
        
        # Get unique locations
        unique_locations = {}
        for key, location in glossary.locations.items():
            if location.colloquial_name not in unique_locations:
                unique_locations[location.colloquial_name] = {
                    "colloquial_name": location.colloquial_name,
                    "full_name": location.full_name,
                    "country_code": location.country_code_iso,
                    "region": location.region,
                    "synonyms": location.synonyms,
                    "abbreviations": location.abbreviations
                }
        
        return {
            "locations": list(unique_locations.values()),
            "total_count": len(unique_locations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location glossary: {str(e)}")

@app.get("/glossary/age_terms")
async def get_age_glossary():
    """Get all age term mappings from the glossary"""
    try:
        from backend.glossary import get_glossary
        glossary = get_glossary()
        
        # Get unique age terms
        unique_age_terms = {}
        for key, age_term in glossary.age_terms.items():
            if age_term.term not in unique_age_terms:
                unique_age_terms[age_term.term] = {
                    "term": age_term.term,
                    "numerical_range": age_term.numerical_range,
                    "synonyms": age_term.synonyms
                }
        
        return {
            "age_terms": list(unique_age_terms.values()),
            "total_count": len(unique_age_terms)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get age glossary: {str(e)}")

# ===== THRESHOLD MANAGEMENT ENDPOINTS =====

@app.get("/thresholds")
async def get_threshold_rules():
    """Get all threshold rules and their configuration"""
    try:
        from backend.glossary import get_glossary
        glossary = get_glossary()
        
        threshold_rules = glossary.get_all_threshold_rules()
        
        return {
            "threshold_rules": {
                rule_name: {
                    "confidence_threshold": rule.confidence_threshold,
                    "escalation_rule": rule.escalation_rule,
                    "description": rule.description,
                    "categories": rule.categories,
                    "priority": rule.priority,
                    "below_threshold_action": rule.below_threshold_action
                } for rule_name, rule in threshold_rules.items()
            },
            "total_rules": len(threshold_rules),
            "system_version": "1.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threshold rules: {str(e)}")

@app.get("/thresholds/{rule_name}")
async def get_threshold_rule(rule_name: str):
    """Get a specific threshold rule by name"""
    try:
        from backend.glossary import get_glossary
        glossary = get_glossary()
        
        rule = glossary.get_threshold_rule(rule_name)
        
        if not rule:
            raise HTTPException(status_code=404, detail=f"Threshold rule '{rule_name}' not found")
        
        return {
            "rule_name": rule_name,
            "confidence_threshold": rule.confidence_threshold,
            "escalation_rule": rule.escalation_rule,
            "description": rule.description,
            "categories": rule.categories,
            "priority": rule.priority,
            "below_threshold_action": rule.below_threshold_action
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threshold rule: {str(e)}")

@app.put("/thresholds/{rule_name}")
async def update_threshold_rule(rule_name: str, rule_update: ThresholdRuleUpdate):
    """Update or create a threshold rule"""
    try:
        from backend.glossary import get_glossary, ThresholdRule
        glossary = get_glossary()
        
        # Validate threshold value
        if not (0.0 <= rule_update.confidence_threshold <= 1.0):
            raise HTTPException(status_code=400, detail="Confidence threshold must be between 0.0 and 1.0")
        
        # Validate escalation rule
        valid_escalation_rules = ["human_review", "auto_ok", "ignore"]
        if rule_update.escalation_rule not in valid_escalation_rules:
            raise HTTPException(status_code=400, detail=f"Invalid escalation rule. Must be one of: {valid_escalation_rules}")
        
        # Validate priority
        valid_priorities = ["low", "medium", "high", "critical"]
        if rule_update.priority not in valid_priorities:
            raise HTTPException(status_code=400, detail=f"Invalid priority. Must be one of: {valid_priorities}")
        
        # Validate below_threshold_action
        valid_actions = ["human", "auto_ok", "ignore"]
        if rule_update.below_threshold_action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid below_threshold_action. Must be one of: {valid_actions}")
        
        # Create the threshold rule
        threshold_rule = ThresholdRule(
            confidence_threshold=rule_update.confidence_threshold,
            escalation_rule=rule_update.escalation_rule,
            description=rule_update.description,
            categories=rule_update.categories,
            priority=rule_update.priority,
            below_threshold_action=rule_update.below_threshold_action
        )
        
        # Update the rule
        success = glossary.update_threshold_rule(rule_name, threshold_rule)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update threshold rule")
        
        return {
            "message": f"Threshold rule '{rule_name}' updated successfully",
            "rule_name": rule_name,
            "updated_rule": {
                "confidence_threshold": threshold_rule.confidence_threshold,
                "escalation_rule": threshold_rule.escalation_rule,
                "description": threshold_rule.description,
                "categories": threshold_rule.categories,
                "priority": threshold_rule.priority,
                "below_threshold_action": threshold_rule.below_threshold_action
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update threshold rule: {str(e)}")

@app.post("/thresholds/{rule_name}/evaluate")
async def evaluate_threshold(rule_name: str, confidence: float, category: str = None):
    """Evaluate a confidence score against a threshold rule"""
    try:
        from backend.glossary import get_glossary
        glossary = get_glossary()
        
        # Validate confidence value
        if not (0.0 <= confidence <= 1.0):
            raise HTTPException(status_code=400, detail="Confidence must be between 0.0 and 1.0")
        
        # If category is provided, use it; otherwise use first category from the rule
        if not category:
            rule = glossary.get_threshold_rule(rule_name)
            if not rule or not rule.categories:
                raise HTTPException(status_code=400, detail="Category must be provided if rule has no default categories")
            category = rule.categories[0]
        
        # Evaluate the threshold
        decision = glossary.evaluate_threshold(category, confidence)
        
        return {
            "threshold_rule_name": decision.threshold_rule_name,
            "category": category,
            "confidence": decision.confidence,
            "threshold": decision.threshold,
            "meets_threshold": decision.meets_threshold,
            "escalation_action": decision.escalation_action,
            "priority": decision.priority,
            "reasoning": decision.reasoning,
            "evaluated_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate threshold: {str(e)}")

@app.get("/thresholds/categories/mapping")
async def get_category_threshold_mapping():
    """Get mapping of categories to their threshold rules"""
    try:
        from backend.glossary import get_glossary
        glossary = get_glossary()
        
        threshold_rules = glossary.get_all_threshold_rules()
        category_mapping = {}
        
        for rule_name, rule in threshold_rules.items():
            for category in rule.categories:
                category_mapping[category] = {
                    "rule_name": rule_name,
                    "threshold": rule.confidence_threshold,
                    "escalation_rule": rule.escalation_rule,
                    "priority": rule.priority,
                    "description": rule.description
                }
        
        return {
            "category_mapping": category_mapping,
            "total_categories": len(category_mapping),
            "total_rules": len(threshold_rules)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category mapping: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
