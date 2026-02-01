# Geo-Compliance Feature Classification System

A production-ready system for automated detection and classification of software features requiring geographic-specific regulatory compliance. 

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technical Architecture](#technical-architecture)
- [System Components](#system-components)
- [Data Flow](#data-flow)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Supported Regulations](#supported-regulations)
- [Troubleshooting](#troubleshooting)

---

## Overview

This system automates the classification of software features to determine if they require geo-specific compliance logic. It combines multiple AI/ML techniques including:

- **Named Entity Recognition (NER)** for extracting locations, ages, and regulatory terminology
- **RAG (Retrieval-Augmented Generation)** with FAISS vector search for regulation matching
- **LLM Integration** for nuanced compliance analysis
- **Multi-stage confidence scoring** with category-specific thresholds
- **Human-in-the-loop** escalation for ambiguous cases

### Problem Statement

When developing global software products, features may trigger different regulatory requirements based on user location:
- Age verification in the EU (GDPR) vs. US states (COPPA, CA Kids Act)
- Data residency requirements (EU, China, Russia)
- Content moderation rules (EU DSA)
- Child safety protections (NCMEC reporting)

This system automatically identifies which features need geo-specific implementation.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Stage Classification** | Preprocessing → NER → LLM → Confidence Scoring pipeline |
| **Dual Confidence Scoring** | Combines LLM confidence (70%) with Regex/NER confidence (30%) |
| **Category-Specific Thresholds** | Different confidence requirements for legal (90%) vs. business (70%) features |
| **Ambiguity Detection** | Identifies unclear cases and flags for human review |
| **RAG-Enhanced Analysis** | Semantic search across 8 regulation documents |
| **Glossary System** | 1,500+ term mappings for locations, ages, and regulatory terminology |
| **Geo-Access Control** | Real-time geographic access enforcement |
| **Audit Trail** | Complete logging to Supabase for compliance |
| **Feedback Loop** | Self-evolution through human corrections |

---

## Technical Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  Streamlit Web UI          │  REST API Clients    │  CSV Batch Upload   │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API LAYER (FastAPI)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  /classify              │  /classify_enhanced    │  /check_access       │
│  /batch_classify        │  /stats                │  /logs               │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CLASSIFICATION PIPELINE                           │
├───────────────┬───────────────┬───────────────┬─────────────────────────┤
│ Preprocessing │ NER/Regex     │ LLM Analysis  │ Confidence Scoring      │
│ & Tokenization│ Detection     │ + RAG Context │ + Decision Engine       │
└───────────────┴───────────────┴───────────────┴─────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Glossary (1,500+ terms)   │  RAG Index (FAISS)  │  Regulation Docs     │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        INFRASTRUCTURE LAYER                              │
├─────────────────────────────────────────────────────────────────────────┤
│  Supabase (PostgreSQL)     │  Feedback System    │  Monitoring          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Classification Pipeline Detail

```
Input Feature (title + description)
         │
         ▼
┌─────────────────────────┐
│   1. PREPROCESSING      │  • Text normalization
│                         │  • Tokenization
│                         │  • Entity extraction
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   2. NER/REGEX STAGE    │  • HuggingFace NER model
│   (95% confidence cases)│  • Regex pattern matching
│                         │  • Location/Age/Term detection
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   3. GLOSSARY           │  • Location standardization (US→United States)
│   STANDARDIZATION       │  • Age normalization (teens→13-19)
│                         │  • Terminology mapping (GDPR→EU data protection)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   4. RAG RETRIEVAL      │  • FAISS vector similarity search
│                         │  • Fetch relevant regulation context
│                         │  • Sentence-transformer embeddings
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   5. LLM ANALYSIS       │  • Ollama (Llama 2) or rule-based fallback
│                         │  • Regulatory compliance determination
│                         │  • Risk assessment generation
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   6. CONFIDENCE         │  • Weighted scoring: LLM (0.7) + NER (0.3)
│   CALCULATION           │  • Low (0-0.3) / Medium (0.31-0.7) / High (0.71-1.0)
│                         │  • Cross-validation adjustments
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   7. DECISION ENGINE    │  • Category-specific threshold application
│                         │  • Escalation rule enforcement
│                         │  • Human review flagging
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   8. OUTPUT             │  • Classification result
│                         │  • Applicable regulations
│                         │  • Confidence breakdown
│                         │  • Recommended actions
└─────────────────────────┘
```

---

## System Components

### Core Classification (`src/backend/core/`)

| Component | File | Purpose |
|-----------|------|---------|
| **Enhanced Classifier** | `enhanced_classifier.py` | Main multi-stage classification pipeline |
| **LLM Classifier** | `llm_classifier.py` | LLM-based regulatory analysis with Ollama |
| **Preprocessing** | `preprocessing.py` | Text normalization, NER, entity extraction |
| **Confidence Scoring** | `confidence_scoring.py` | Weighted confidence calculation |

### Knowledge Management (`src/backend/knowledge/`)

| Component | File | Purpose |
|-----------|------|---------|
| **Glossary** | `glossary.py` | 1,500+ term mappings for standardization |
| **Glossary Data** | `glossary_data.json` | Location, age, terminology mappings |
| **RAG Loader** | `rag_loader.py` | FAISS vector index for regulation search |

### Compliance Engine (`src/backend/compliance/`)

| Component | File | Purpose |
|-----------|------|---------|
| **Geo-Compliance** | `geo_compliance.py` | Geographic access control logic |
| **Ambiguity Handler** | `ambiguity_handler.py` | Uncertainty detection and disambiguation |
| **Decision Engine** | `enhanced_decision_engine.py` | Category-specific threshold decisions |

### Infrastructure (`src/backend/infrastructure/`)

| Component | File | Purpose |
|-----------|------|---------|
| **Supabase Client** | `supabase_client.py` | Database operations and logging |
| **Feedback System** | `feedback_system.py` | Human feedback processing and learning |
| **Monitoring** | `monitoring.py` | Health checks and performance metrics |

### Confidence Thresholds

The system uses category-specific confidence thresholds defined in `config/threshold_config.json`:

| Category | Threshold | Escalation | Examples |
|----------|-----------|------------|----------|
| **Legal Compliance** | 90% | Human Review | GDPR, COPPA, DSA, HIPAA |
| **Safety/Health** | 85% | Human Review | Child protection, CSAM, age gates |
| **Data Residency** | 88% | Human Review | Data localization, storage |
| **Tax Compliance** | 87% | Human Review | VAT, tax ID collection |
| **Business Analytics** | 70% | Auto-OK | A/B testing, segmentation |
| **Internal Features** | 60% | Ignore | Performance, caching |

---

## Data Flow

### Single Feature Classification

```
1. User submits feature via API/UI
         │
2. FastAPI receives POST /classify_enhanced
         │
3. EnhancedGeoComplianceClassifier.classify()
         │
4. Preprocessing extracts entities (locations, ages, terms)
         │
5. Glossary standardizes entities
         │
6. RAG retrieves relevant regulation context
         │
7. LLM/Rule-based analysis determines compliance needs
         │
8. Confidence scorer calculates weighted score
         │
9. Decision engine applies category thresholds
         │
10. Result logged to Supabase
         │
11. Response returned with classification + confidence
```

### Geo-Access Control Flow

```
1. User/Service requests access: POST /check_access
         │
2. GeoComplianceEngine.check_access(user_id, feature, country)
         │
3. Fetch rules from Supabase geo_rules table
         │
4. Evaluate: Is country in allowed_countries? blocked_countries?
         │
5. Log access attempt to access_logs table
         │
6. Return access decision with reason
```

---

## Project Structure

```
Qn3/
├── config/                              # Configuration
│   └── threshold_config.json            # Category-specific thresholds
│
├── src/                                 # Source code
│   ├── backend/
│   │   ├── api/
│   │   │   └── main.py                  # FastAPI application & endpoints
│   │   ├── core/
│   │   │   ├── enhanced_classifier.py   # Multi-stage classification
│   │   │   ├── llm_classifier.py        # LLM integration
│   │   │   ├── preprocessing.py         # NER & text processing
│   │   │   └── confidence_scoring.py    # Confidence calculation
│   │   ├── knowledge/
│   │   │   ├── glossary.py              # Term standardization
│   │   │   ├── glossary_data.json       # 1,500+ term mappings
│   │   │   └── rag_loader.py            # FAISS vector search
│   │   ├── compliance/
│   │   │   ├── geo_compliance.py        # Geo-access control
│   │   │   ├── ambiguity_handler.py     # Uncertainty handling
│   │   │   └── enhanced_decision_engine.py  # Threshold decisions
│   │   └── infrastructure/
│   │       ├── supabase_client.py       # Database client
│   │       ├── feedback_system.py       # Human feedback loop
│   │       └── monitoring.py            # Health & metrics
│   └── frontend/
│       └── app.py                       # Streamlit web interface
│
├── regulations/                         # Compliance documents (8 files)
│   ├── gdpr.txt                         # EU General Data Protection
│   ├── coppa.txt                        # Children's Online Privacy
│   ├── eu_dsa.txt                       # EU Digital Services Act
│   ├── ccpa.txt                         # California Consumer Privacy
│   ├── ca_kids_act.txt                  # California Age-Appropriate Design
│   ├── ut_social_media_act.txt          # Utah Social Media Regulation
│   ├── fl_minor_protections.txt         # Florida Minor Protection
│   └── us_ncmec_reporting.txt           # NCMEC Reporting Requirements
│
├── data/
│   ├── input/                           # Input CSV files
│   └── output/                          # Classification results
│
├── docker/                              # Docker configuration
│   ├── Dockerfile.backend               # Full backend with NLP
│   ├── Dockerfile.backend.simple        # Lightweight backend
│   ├── Dockerfile.frontend              # Streamlit container
│   └── docker-compose.yml               # Service orchestration
│
├── scripts/
│   ├── analysis/                        # Analysis scripts
│   ├── demos/                           # Demo scripts
│   └── utils/                           # Utility scripts
│
├── tests/                               # Test suite
├── docs/                                # Documentation
├── requirements.txt                     # Python dependencies
└── .env                                 # Environment variables
```

---

## Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- Supabase account (for production)

### Option 1: Docker (Recommended)

```bash
# Clone and navigate to project
cd Qn3

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Build and run
cd docker
docker-compose up --build
```

**Services:**
- Backend API: http://localhost:8001
- Frontend UI: http://localhost:8501
- API Docs: http://localhost:8001/docs

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn src.backend.api.main:app --reload --port 8000

# Start frontend (new terminal)
streamlit run src/frontend/app.py
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# Required for Supabase integration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Optional: LLM integration
OPENAI_API_KEY=your-openai-key      # For GPT fallback
OLLAMA_URL=http://localhost:11434   # For local Llama 2

# System configuration
ENVIRONMENT=development
API_PORT=8000
STREAMLIT_PORT=8501
RAG_MODEL=all-MiniLM-L6-v2
```

### Supabase Database Schema

```sql
-- Classification results storage
CREATE TABLE classification_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    needs_geo_logic BOOLEAN NOT NULL,
    confidence FLOAT NOT NULL,
    reasoning TEXT NOT NULL,
    regulations TEXT[] DEFAULT '{}',
    risk_level TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Geo-compliance access rules
CREATE TABLE geo_rules (
    feature_name TEXT PRIMARY KEY,
    allowed_countries TEXT[],
    blocked_countries TEXT[]
);

-- Access audit logs
CREATE TABLE access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    country TEXT NOT NULL,
    access_granted BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## API Reference

### Classification Endpoints

#### `POST /classify`
Basic feature classification.

**Request:**
```json
{
  "title": "User Age Verification",
  "description": "Verify user age during registration using ID validation"
}
```

**Response:**
```json
{
  "needs_geo_logic": true,
  "confidence": 0.92,
  "reasoning": "Age verification triggers COPPA, GDPR, and state-specific requirements",
  "applicable_regulations": [
    {"name": "COPPA", "jurisdiction": "US", "relevance": "high"},
    {"name": "GDPR", "jurisdiction": "EU", "relevance": "high"}
  ],
  "risk_assessment": "high",
  "regulatory_requirements": ["Parental consent for under-13", "Age gate implementation"],
  "evidence_sources": ["coppa.txt", "gdpr.txt"],
  "recommended_actions": ["Implement age verification flow", "Add parental consent mechanism"]
}
```

#### `POST /classify_enhanced`
Full multi-stage classification with detailed confidence breakdown.

**Response includes:**
- `primary_confidence` (LLM)
- `secondary_confidence` (NER/Regex)
- `overall_confidence` (weighted)
- `confidence_breakdown` (per-factor scores)
- `needs_human_review` (boolean)
- `intervention_priority` (low/medium/high/critical)
- `categories_detected` (legal_compliance, safety, etc.)
- `applicable_threshold` (category-specific)

#### `POST /batch_classify`
Upload CSV for bulk classification.

**Request:** Multipart form with CSV file (columns: `title`, `description`)

**Response:** CSV download with added columns for classification results.

### Geo-Access Endpoints

#### `POST /check_access`
Check geographic access permission.

**Request:**
```json
{
  "user_id": "user123",
  "feature_name": "live_streaming",
  "country": "CN"
}
```

**Response:**
```json
{
  "access_granted": false,
  "reason": "Access denied: 'CN' is in blocked countries for 'live_streaming'"
}
```

#### `GET /logs`
Retrieve access audit logs.

**Query params:** `limit`, `offset`, `user_id`, `feature_name`

### System Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with component status |
| `/regulations` | GET | List available regulation documents |
| `/stats` | GET | Classification statistics |
| `/search_regulations` | POST | Semantic search across regulations |

---

## Usage Examples

### Python Client

```python
import requests

# Single classification
response = requests.post("http://localhost:8000/classify_enhanced", json={
    "title": "Location-based Content Filtering",
    "description": "Filter content based on user's geographic location and local laws"
})
result = response.json()

print(f"Needs geo-logic: {result['needs_geo_logic']}")
print(f"Confidence: {result['overall_confidence']:.2%}")
print(f"Risk level: {result['risk_assessment']}")
print(f"Regulations: {[r['name'] for r in result['applicable_regulations']]}")
```

### Batch Processing

```python
import pandas as pd

# Prepare features
features = pd.DataFrame([
    {"title": "Age Gate", "description": "Verify user is over 18"},
    {"title": "Cache Layer", "description": "Redis caching for performance"},
    {"title": "GDPR Consent", "description": "Cookie consent banner for EU users"}
])
features.to_csv("features.csv", index=False)

# Upload for batch processing
with open("features.csv", "rb") as f:
    response = requests.post(
        "http://localhost:8000/batch_classify",
        files={"file": f}
    )

# Results returned as CSV
with open("results.csv", "wb") as f:
    f.write(response.content)
```

### Web Interface

1. Navigate to http://localhost:8501
2. Select mode: Single Feature / Batch Upload / Geo-Access
3. Enter feature details or upload CSV
4. View classification results with confidence breakdown
5. Check classification history and analytics

---

## Supported Regulations

| Regulation | Jurisdiction | Coverage |
|------------|--------------|----------|
| **GDPR** | European Union | Data protection, privacy rights, consent |
| **COPPA** | United States | Children's online privacy (under 13) |
| **CCPA** | California, US | Consumer privacy rights |
| **EU DSA** | European Union | Digital services, content moderation |
| **CA Kids Act** | California, US | Age-appropriate design for minors |
| **UT Social Media Act** | Utah, US | Parental consent, minor protections |
| **FL Minor Protections** | Florida, US | Social media age verification |
| **NCMEC Reporting** | United States | Child exploitation material reporting |

### Adding New Regulations

1. Create a `.txt` file in `regulations/` directory
2. Follow the format:
```
Regulation Name - Geographic Scope

Overview of the regulation and its purpose.

Key Requirements:
- Requirement 1: Description
- Requirement 2: Description

Applies to features involving: [feature types]

Penalties: [non-compliance consequences]
```
3. Restart the system to rebuild the RAG index

---

## Troubleshooting

### Common Issues

**Import errors after reorganization:**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/Qn3
```

**RAG index issues:**
```bash
# Force rebuild
rm -f regulation_index.faiss regulation_metadata.pkl
# Restart the application
```

**Supabase connection fails:**
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
- System falls back to mock mode automatically

**Docker build fails:**
```bash
# Clean rebuild
docker-compose down
docker system prune -f
docker-compose up --build
```

**NER model download issues:**
```bash
# Pre-download HuggingFace models
python -c "from transformers import AutoTokenizer, AutoModelForTokenClassification; AutoTokenizer.from_pretrained('dslim/bert-base-NER'); AutoModelForTokenClassification.from_pretrained('dslim/bert-base-NER')"
```

---

## Performance

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Single classification | <500ms | - |
| RAG retrieval | <50ms | - |
| Batch processing | - | ~100 features/min |
| Geo-access check | <100ms | - |

---

## License

Hackathon prototype - TikTok Tech Jam 2024

---

## Contributors

Built with FastAPI, Streamlit, FAISS, HuggingFace Transformers, and Supabase.
