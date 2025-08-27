from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
import csv
import io
from typing import List, Union
import json
from datetime import datetime, timedelta
import os
from backend.llm_classifier import get_classifier, LLMClassificationResult
from backend.rag_loader import get_rag_instance
from backend.auth import (
    get_current_user, get_current_admin_user, authenticate_user, 
    create_access_token, check_rate_limit, User, Token
)
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI(title="Geo-Compliance Detection API", version="1.0.0")

# Pydantic models for request/response
class FeatureArtifact(BaseModel):
    title: str
    description: str

class ComplianceResult(BaseModel):
    needs_geo_logic: bool
    confidence: float
    reasoning: str
    regulations: List[str]
    risk_level: str  # "low", "medium", "high"
    specific_requirements: List[str]

class BatchResult(BaseModel):
    total_processed: int
    results: List[dict]

def classify_feature(title: str, description: str) -> ComplianceResult:
    """
    Classify feature using LLM + RAG for geo-compliance requirements.
    Falls back to enhanced mock classification if LLM is unavailable.
    """
    classifier = get_classifier()
    llm_result = classifier.classify_feature(title, description)
    
    # Convert LLM result to API response format
    return ComplianceResult(
        needs_geo_logic=llm_result.needs_geo_logic,
        confidence=llm_result.confidence,
        reasoning=llm_result.reasoning,
        regulations=llm_result.regulations,
        risk_level=llm_result.risk_level,
        specific_requirements=llm_result.specific_requirements
    )

def log_result(title: str, description: str, result: ComplianceResult):
    """Log classification results for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "title": title,
        "description": description,
        "needs_geo_logic": result.needs_geo_logic,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "regulations": "; ".join(result.regulations),
        "risk_level": result.risk_level,
        "specific_requirements": "; ".join(result.specific_requirements)
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

@app.get("/")
async def root():
    return {"message": "Geo-Compliance Detection API", "version": "1.0.0"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/classify", response_model=ComplianceResult)
async def classify_single_feature(
    feature: FeatureArtifact,
    current_user: User = Depends(get_current_user)
):
    """
    Classify a single feature artifact for geo-compliance requirements.
    
    Returns:
    - needs_geo_logic: true/false/"uncertain"
    - reasoning: explanation for the classification
    - regulations: list of relevant regulations
    """
    try:
        # Check rate limit
        check_rate_limit(current_user.username)
        
        result = classify_feature(feature.title, feature.description)
        
        # Log result for audit trail
        log_result(feature.title, feature.description, result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/batch_classify")
async def batch_classify_features(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
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
        # Check rate limit
        check_rate_limit(current_user.username)
        
        # Read uploaded CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        if 'title' not in df.columns or 'description' not in df.columns:
            raise HTTPException(
                status_code=400, 
                detail="CSV must contain 'title' and 'description' columns"
            )
        
        # Process each row
        results = []
        for _, row in df.iterrows():
            title = str(row['title']) if pd.notna(row['title']) else ""
            description = str(row['description']) if pd.notna(row['description']) else ""
            
            # Classify the feature
            classification = classify_feature(title, description)
            
            # Log result
            log_result(title, description, classification)
            
            # Add classification results to row
            result_row = row.to_dict()
            result_row.update({
                'needs_geo_logic': classification.needs_geo_logic,
                'confidence': classification.confidence,
                'reasoning': classification.reasoning,
                'regulations': "; ".join(classification.regulations),
                'risk_level': classification.risk_level,
                'specific_requirements': "; ".join(classification.specific_requirements),
                'classified_at': datetime.now().isoformat()
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

@app.get("/regulations")
async def list_regulations(current_user: User = Depends(get_current_user)):
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
async def search_regulations(
    query: str,
    current_user: User = Depends(get_current_user)
):
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

@app.get("/stats")
async def get_statistics(current_user: User = Depends(get_current_user)):
    """Get classification statistics"""
    try:
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
