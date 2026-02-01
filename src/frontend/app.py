import streamlit as st
import requests
import pandas as pd
import json
import io
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Geo-Compliance Detection",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced UI Styling with Proper Contrast
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling - Simple and Clean */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
    }
    
    /* Force most text to be visible */
    .stApp, .stApp * {
        color: #1a202c !important;
    }
    
    /* Main content container with gradient background for white text areas */
    .main .block-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        color: #1a202c !important;
    }
    
    /* White text for input areas */
    .stTextInput label, .stTextArea label {
        color: white !important;
    }
    
    /* White text for form inputs when they have content */
    .stTextInput input, .stTextArea textarea {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Results area with white background for dark text */
    .results-container {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .results-container * {
        color: #1a202c !important;
    }
    
    /* Header styling - Simplified */
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #4c51bf 0%, #667eea 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header * {
        color: white !important;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: white !important;
    }
    
    .main-header h2 {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: white !important;
        opacity: 0.95;
    }
    
    .main-header p {
        font-size: 1.1rem;
        font-weight: 400;
        color: white !important;
        opacity: 0.95;
    }
    
    /* Simplified button styling */
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Enhanced Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2d3748 0%, #4a5568 100%);
        border-right: 2px solid #667eea;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar content */
    .css-1d391kg .css-1y4p8pa {
        padding: 1.5rem 1rem;
    }
    
    /* Sidebar title styling */
    .css-1d391kg h1 {
        color: #ffffff !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-bottom: 1.5rem !important;
        text-align: center !important;
        padding: 0.75rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Navigation selectbox styling */
    .css-1d391kg .stSelectbox > label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Selectbox container */
    .css-1d391kg .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .css-1d391kg .stSelectbox > div > div:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Selectbox text */
    .css-1d391kg .stSelectbox input {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Dropdown arrow */
    .css-1d391kg .stSelectbox svg {
        fill: #e2e8f0 !important;
    }
    
    /* Sidebar buttons (if any) */
    .css-1d391kg .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 0.25rem 0 !important;
    }
    
    .css-1d391kg .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Sidebar text and labels */
    .css-1d391kg p, .css-1d391kg span, .css-1d391kg div {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar metrics and info boxes */
    .css-1d391kg .metric-container {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 6px !important;
        padding: 0.75rem !important;
        margin: 0.5rem 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Sidebar markdown content */
    .css-1d391kg .markdown-text-container {
        color: #cbd5e0 !important;
    }
    
    /* Alternative sidebar class names (Streamlit versions vary) */
    .css-17eq0hr, .css-1lcbmhc, .css-1y4p8pa {
        background: linear-gradient(180deg, #2d3748 0%, #4a5568 100%) !important;
    }
    
    /* Additional sidebar styling for different Streamlit versions */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #4a5568 100%) !important;
        border-right: 2px solid #667eea !important;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
        padding-top: 2rem !important;
    }
    
    /* Sidebar navigation title with enhanced styling */
    section[data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-bottom: 1.5rem !important;
        text-align: center !important;
        padding: 0.75rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        margin-left: 0.5rem !important;
        margin-right: 0.5rem !important;
    }
    
    /* Sidebar selectbox improvements */
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.75rem !important;
        letter-spacing: 0.025em !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.25), 0 4px 8px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Sidebar selectbox text */
    section[data-testid="stSidebar"] .stSelectbox input {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    
    /* Sidebar selectbox dropdown arrow */
    section[data-testid="stSidebar"] .stSelectbox svg {
        fill: #e2e8f0 !important;
        transition: fill 0.2s ease !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox:hover svg {
        fill: #ffffff !important;
    }
    
    /* Enhanced hover effects and visual feedback */
    section[data-testid="stSidebar"] .stSelectbox {
        transition: all 0.2s ease !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox:hover {
        transform: translateX(2px) !important;
    }
    
    /* Sidebar general text styling */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] div {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar buttons styling */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px) translateX(2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Sidebar metrics and info styling */
    section[data-testid="stSidebar"] .metric-container,
    section[data-testid="stSidebar"] .stMetric {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        margin: 0.5rem 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        transition: all 0.3s ease !important;
    }
    
    section[data-testid="stSidebar"] .metric-container:hover,
    section[data-testid="stSidebar"] .stMetric:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(102, 126, 234, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Sidebar markdown and text content */
    section[data-testid="stSidebar"] .markdown-text-container {
        color: #cbd5e0 !important;
        line-height: 1.6 !important;
    }
    
    /* Sidebar dividers */
    section[data-testid="stSidebar"] hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Visual hierarchy improvements */
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    
    /* Sidebar icon enhancements */
    section[data-testid="stSidebar"] .stSelectbox::before {
        content: "🧭" !important;
        margin-right: 0.5rem !important;
        font-size: 1.1rem !important;
    }
    
    /* Navigation section styling */
    section[data-testid="stSidebar"] > div:first-child {
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding-bottom: 1rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Sidebar scrollbar styling */
    section[data-testid="stSidebar"]::-webkit-scrollbar {
        width: 6px !important;
    }
    
    section[data-testid="stSidebar"]::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 3px !important;
    }
    
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5) !important;
        border-radius: 3px !important;
        transition: background 0.3s ease !important;
    }
    
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.7) !important;
    }
    
    /* Responsive sidebar adjustments */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.2) !important;
        }
        
        section[data-testid="stSidebar"] h1 {
            font-size: 1.2rem !important;
            padding: 0.5rem !important;
        }
    }
    
    /* Polish for selected state */
    section[data-testid="stSidebar"] .stSelectbox > div > div[aria-expanded="true"] {
        background: rgba(102, 126, 234, 0.2) !important;
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Animation for loading states */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Backend API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def import_backend_decision_engine():
    """Helper function to import the backend decision engine with proper path setup"""
    try:
        import sys
        import os
        
        # Get the current file's directory (frontend folder)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to get project root
        project_root = os.path.dirname(current_dir)
        
        # Debug information
        debug_info = {
            'current_dir': current_dir,
            'project_root': project_root,
            'backend_exists': os.path.exists(os.path.join(project_root, 'backend')),
            'init_exists': os.path.exists(os.path.join(project_root, 'backend', '__init__.py')),
            'engine_exists': os.path.exists(os.path.join(project_root, 'backend', 'enhanced_decision_engine.py')),
            'cwd': os.getcwd(),
            'project_in_path': project_root in sys.path
        }
        
        # Try multiple potential project roots
        potential_roots = [
            project_root,  # Standard: one level up from frontend
            os.getcwd(),   # Current working directory
            os.path.dirname(os.getcwd()),  # One level up from CWD
            '/'.join(current_dir.split('/')[:-1]),  # Alternative path calculation
        ]
        
        backend_found = False
        working_root = None
        
        for root in potential_roots:
            if os.path.exists(os.path.join(root, 'backend', '__init__.py')):
                working_root = root
                backend_found = True
                break
        
        if not backend_found:
            st.error("❌ Could not locate backend directory with __init__.py")
            if st.checkbox("Show Debug Info", key="debug_backend_search"):
                st.json(debug_info)
                st.write("**Potential roots checked:**")
                for i, root in enumerate(potential_roots):
                    backend_path = os.path.join(root, 'backend')
                    st.write(f"{i+1}. `{root}` → backend exists: {os.path.exists(backend_path)}")
            return None
        
        # Add working root to sys.path if not already there
        if working_root not in sys.path:
            sys.path.insert(0, working_root)
        
        # Try importing the backend module
        from src.backend.compliance.enhanced_decision_engine import EnhancedDecisionEngine
        return EnhancedDecisionEngine()
        
    except ImportError as first_import_error:
        # Fallback: Try simpler import with current directory
        try:
            import sys
            import os
            
            # Simple fallback: Add current directory to path
            current_cwd = os.getcwd()
            if current_cwd not in sys.path:
                sys.path.insert(0, current_cwd)
                
            from src.backend.compliance.enhanced_decision_engine import EnhancedDecisionEngine
            return EnhancedDecisionEngine()
            
        except ImportError:
            # Both methods failed, show detailed error
            st.error(f"❌ Could not import backend module: {first_import_error}")
            st.info("💡 Make sure you're running the app from the project root directory with: `streamlit run frontend/app.py`")
            
            if st.checkbox("Show Detailed Debug Info", key="debug_import_error"):
                st.write("**Debug Information:**")
                st.write(f"- Current working directory: {os.getcwd()}")
                st.write(f"- Frontend file location: {current_dir}")
                st.write(f"- Calculated project root: {working_root}")
                st.write(f"- Backend directory exists: {os.path.exists(os.path.join(working_root or project_root, 'backend'))}")
                st.write(f"- Backend __init__.py exists: {os.path.exists(os.path.join(working_root or project_root, 'backend', '__init__.py'))}")
                st.write("**Python path (first 5 entries):**")
                for i, path in enumerate(sys.path[:5]):
                    st.write(f"  {i}: {path}")
            
            return None
    except Exception as e:
        # General error handling
        st.error(f"❌ Error setting up decision engine: {e}")
        st.write(f"Error type: {type(e).__name__}")
        return None

def call_api(endpoint: str, data=None, files=None, headers=None):
    """Make API calls to the backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        # Set default headers
        if headers is None:
            headers = {}
        
        if files:
            response = requests.post(url, files=files, headers=headers)
        elif data:
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Make sure the FastAPI server is running on http://localhost:8000")
        st.info("💡 Run: `uvicorn backend.main:app --reload`")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {e}")
        return None



def display_detailed_confidence_breakdown(result: dict):
    """Display detailed confidence breakdown with visual indicators and explanations"""
    
    confidence_breakdown = result.get('confidence_breakdown', {})
    standardized_entities = result.get('standardized_entities', {})
    
    # Overall confidence for reference
    overall_confidence = result.get('overall_confidence', result.get('confidence', 0))
    primary_confidence = result.get('primary_confidence', 0)
    secondary_confidence = result.get('secondary_confidence', 0)
    
    st.subheader("🎯 Confidence Explainability")
    st.markdown("**Detailed breakdown of analysis confidence across different components:**")
    
    # Entity Detection Component
    entity_confidence_scores = standardized_entities.get('confidence_scores', {})
    entity_avg = sum(entity_confidence_scores.values()) / len(entity_confidence_scores) if entity_confidence_scores else 0.5
    entity_percentage = entity_avg * 100
    
    if entity_percentage >= 85:
        entity_icon = "✅"
        entity_status = "High Confidence"
    elif entity_percentage >= 60:
        entity_icon = "⚠️"
        entity_status = "Medium Confidence"
    else:
        entity_icon = "❌"
        entity_status = "Low Confidence"
    
    st.markdown(f"**Entity Detection {entity_icon} ({entity_percentage:.0f}%)** - {entity_status}")
    
    # Classification Component
    classification_percentage = primary_confidence * 100
    
    if classification_percentage >= 85:
        classification_icon = "✅"
        classification_status = "High Confidence"
    elif classification_percentage >= 60:
        classification_icon = "⚠️"
        classification_status = "Medium Confidence"
    else:
        classification_icon = "❌"
        classification_status = "Low Confidence"
    
    st.markdown(f"**Classification {classification_icon} ({classification_percentage:.0f}%)** - {classification_status}")
    
    # Law Matching Component
    law_matching_percentage = secondary_confidence * 100
    
    if law_matching_percentage >= 85:
        law_icon = "✅"
        law_status = "High Confidence"
    elif law_matching_percentage >= 60:
        law_icon = "⚠️"
        law_status = "Medium Confidence"
    else:
        law_icon = "❌"
        law_status = "Low Confidence"
    
    st.markdown(f"**Law Matching {law_icon} ({law_matching_percentage:.0f}%)** - {law_status}")
    
    # Progress bars for visual representation
    col1, col2, col3 = st.columns(3)
    with col1:
        st.progress(entity_avg)
    with col2:
        st.progress(primary_confidence)
    with col3:
        st.progress(secondary_confidence)
    
    # Explanations for low confidence scores
    explanations = []
    
    # Entity detection explanations
    if entity_percentage < 85:
        locations = standardized_entities.get('locations', [])
        ages = standardized_entities.get('ages', [])
        terminology = standardized_entities.get('terminology', [])
        
        if not locations and not ages and not terminology:
            explanations.append("🔍 **Entity Detection**: No clear regulatory entities (locations, ages, compliance terms) were detected in the feature description.")
        elif entity_confidence_scores.get('location', 0) < 0.7:
            explanations.append("📍 **Location Matching**: Detected locations but uncertain about their regulatory significance.")
        elif entity_confidence_scores.get('age', 0) < 0.7:
            explanations.append("👶 **Age Detection**: Age-related terms found but unclear if they trigger minor protection laws.")
        elif entity_confidence_scores.get('terminology', 0) < 0.7:
            explanations.append("📚 **Terminology**: Regulatory terms detected but not definitively compliance-related.")
    
    # Classification explanations
    if classification_percentage < 85:
        if classification_percentage < 60:
            explanations.append("🤖 **Classification Uncertainty**: LLM analysis shows conflicting signals about regulatory requirements.")
        else:
            explanations.append("🎯 **Classification**: Some indicators suggest regulatory requirements but not definitive enough for high confidence.")
    
    # Law matching explanations  
    if law_matching_percentage < 85:
        applicable_regulations = result.get('applicable_regulations', [])
        if not applicable_regulations:
            explanations.append("⚖️ **Law Matching**: No specific regulations matched to this feature type.")
        elif law_matching_percentage < 60:
            # Look for mismatches in the standardized entities vs regulations
            detected_jurisdictions = []
            for loc in standardized_entities.get('locations', []):
                region = loc.get('region', [])
                if isinstance(region, list):
                    detected_jurisdictions.extend(region)
                elif isinstance(region, str):
                    detected_jurisdictions.append(region)
            
            reg_jurisdictions = [reg.get('jurisdiction', '') for reg in applicable_regulations]
            
            if detected_jurisdictions and reg_jurisdictions:
                # Check for overlap between detected and regulation jurisdictions
                jurisdiction_overlap = any(
                    any(dj.lower() in rj.lower() or rj.lower() in dj.lower() 
                        for dj in detected_jurisdictions if isinstance(dj, str))
                    for rj in reg_jurisdictions if isinstance(rj, str)
                )
                if not jurisdiction_overlap:
                    explanations.append("🌍 **Jurisdiction Mismatch**: Feature mentions specific locations but regulations apply to different jurisdictions.")
            
            detected_ages = standardized_entities.get('ages', [])
            if detected_ages:
                age_regs = [reg for reg in applicable_regulations if 'minor' in reg.get('name', '').lower() or 'child' in reg.get('name', '').lower()]
                if detected_ages and not age_regs:
                    explanations.append("👶 **Age Regulation Gap**: Feature mentions age groups but no age-specific regulations identified.")
        else:
            explanations.append("📋 **Regulation Confidence**: Some applicable laws identified but uncertain about enforcement requirements.")
    
    # Display explanations
    if explanations:
        st.markdown("**🔍 Confidence Explanations:**")
        for explanation in explanations:
            st.info(explanation)
    
    # Technical details in expander
    with st.expander("🔧 Technical Confidence Details"):
        if confidence_breakdown:
            st.markdown("**Confidence Breakdown:**")
            for key, value in confidence_breakdown.items():
                if isinstance(value, (int, float)):
                    st.markdown(f"• **{key.replace('_', ' ').title()}**: {value:.3f}")
        
        if entity_confidence_scores:
            st.markdown("**Entity Detection Scores:**")
            for entity_type, score in entity_confidence_scores.items():
                st.markdown(f"• **{entity_type.title()}**: {score:.3f}")
        
        # Enhanced threshold system details
        if result.get('categories_detected') or result.get('enhanced_decision_result'):
            st.markdown("**🎯 Enhanced Threshold Details:**")
            if result.get('categories_detected'):
                st.markdown(f"• **Categories**: {', '.join(result['categories_detected'])}")
            if result.get('applicable_threshold'):
                st.markdown(f"• **Threshold Applied**: {result['applicable_threshold']:.3f}")
            if result.get('escalation_rule'):
                rule = result['escalation_rule']
                rule_str = rule.value if hasattr(rule, 'value') else str(rule)
                st.markdown(f"• **Escalation Rule**: {rule_str}")


def display_enhanced_threshold_results(result: dict):
    """Display enhanced threshold system results"""
    # This function is called from display_compliance_analysis
    # The actual display logic is now inline in the main function
    pass

def display_all_threshold_values(result: dict):
    """Display comprehensive threshold overview showing all system thresholds"""
    
    st.markdown("### 🎯 **System Threshold Overview**")
    
    # Load threshold configuration
    engine = import_backend_decision_engine()
    if engine:
        threshold_summary = engine.get_threshold_summary()
        
        # Get current feature's information
        current_confidence = result.get('overall_confidence', 0)
        applicable_threshold = result.get('applicable_threshold', 0)
        categories_detected = result.get('categories_detected', [])
        
        # Create columns for threshold display
        st.markdown("**All Category Thresholds:**")
        
        # Display in a nice table format
        threshold_data = []
        
        for category_name, config in threshold_summary.items():
            threshold_val = config['threshold']
            escalation_rule = config['escalation']
            description = config['description']
            
            # Determine if this category applies to current feature
            applies_to_feature = category_name in categories_detected
            meets_threshold = current_confidence >= threshold_val if applies_to_feature else None
            
            # Status indicators
            if applies_to_feature:
                if meets_threshold:
                    status = "✅ PASS"
                    status_color = "green"
                else:
                    status = "❌ FAIL"
                    status_color = "red"
            else:
                status = "➖ N/A"
                status_color = "gray"
            
            threshold_data.append({
                "Category": category_name.replace('_', ' ').title(),
                "Threshold": f"{threshold_val:.1%}",
                "Escalation": escalation_rule.replace('_', ' ').title(),
                "Applies": "🎯" if applies_to_feature else "➖",
                "Status": status,
                "Description": description[:50] + "..." if len(description) > 50 else description
            })
        
        # Sort by threshold value (highest first)
        threshold_data.sort(key=lambda x: float(x['Threshold'].rstrip('%'))/100, reverse=True)
        
        # Display as DataFrame for better formatting
        import pandas as pd
        df = pd.DataFrame(threshold_data)
        
        # Style the dataframe based on status
        def style_row(row):
            if row['Applies'] == "🎯":
                if "PASS" in row['Status']:
                    return ['background-color: #d4edda'] * len(row)
                elif "FAIL" in row['Status']:
                    return ['background-color: #f8d7da'] * len(row)
            return [''] * len(row)
        
        styled_df = df.style.apply(style_row, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # Current feature summary
        st.markdown("---")
        st.markdown("**Current Feature Analysis:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Feature Confidence", 
                f"{current_confidence:.1%}",
                help="Overall confidence score for this feature"
            )
        
        with col2:
            if applicable_threshold > 0:
                st.metric(
                    "Applied Threshold", 
                    f"{applicable_threshold:.1%}",
                    help="Threshold that was applied to this feature"
                )
            else:
                st.metric("Applied Threshold", "N/A")
        
        with col3:
            if categories_detected:
                st.metric(
                    "Categories Detected", 
                    len(categories_detected),
                    help=f"Categories: {', '.join(categories_detected)}"
                )
            else:
                st.metric("Categories Detected", "0")
        
        # Threshold comparison visualization
        if applicable_threshold > 0:
            st.markdown("**Threshold Comparison:**")
            
            # Create a visual comparison
            threshold_pct = applicable_threshold * 100
            confidence_pct = current_confidence * 100
            
            if current_confidence >= applicable_threshold:
                st.success(f"✅ **ABOVE THRESHOLD**: {confidence_pct:.1f}% ≥ {threshold_pct:.1f}%")
            else:
                st.error(f"❌ **BELOW THRESHOLD**: {confidence_pct:.1f}% < {threshold_pct:.1f}%")
            
            # Progress bar comparison
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Feature Confidence:**")
                st.progress(min(current_confidence, 1.0))
            with col_b:
                st.markdown("**Required Threshold:**")
                st.progress(min(applicable_threshold, 1.0))
        
        # Show escalation information
        if result.get('escalation_rule'):
            escalation_rule = result.get('escalation_rule')
            if isinstance(escalation_rule, str):
                rule_name = escalation_rule
            else:
                rule_name = escalation_rule.value if hasattr(escalation_rule, 'value') else str(escalation_rule)
            
            st.markdown("**Escalation Decision:**")
            if 'human_review' in rule_name.lower():
                st.warning(f"⚠️ **HUMAN REVIEW REQUIRED** - {rule_name}")
            elif 'auto_ok' in rule_name.lower():
                st.success(f"✅ **AUTO-APPROVED** - {rule_name}")
            elif 'ignore' in rule_name.lower():
                st.info(f"ℹ️ **IGNORED** - {rule_name}")
            else:
                st.info(f"📋 **{rule_name}**")
        
        # Expandable section with detailed threshold explanations
        with st.expander("📚 **Detailed Threshold Explanations**"):
            st.markdown("""
            **Category Threshold Meanings:**
            
            - **Legal Compliance** (90%): GDPR, HIPAA, COPPA, DSA - Super strict, small errors = high impact
            - **Safety & Health Protection** (85%): Child protection, CSAM reporting, age gates - Strict safety requirements  
            - **Data Residency** (88%): Data localization, storage requirements - Regulatory compliance
            - **Tax Compliance** (87%): VAT, tax ID collection - Financial compliance
            - **Business Analytics** (70%): Product segmentation, A/B testing - Business decisions
            - **Internal Features** (60%): Internal tools, performance optimizations - Low risk
            
            **Escalation Rules:**
            
            - **Human Review**: Critical compliance features requiring manual review
            - **Auto OK**: Can proceed automatically with audit logging
            - **Ignore**: Skip processing, no action required
            """)
            
            st.markdown("**Hybrid Handling:**")
            st.info("When multiple categories apply, the system uses the **strictest (highest) threshold** to ensure compliance.")

def display_compliance_analysis(result: dict, title: str, description: str):
    """Display regulatory compliance analysis with audit-ready information"""
    
    # Determine compliance status and risk assessment styling
    risk_assessment = result.get('risk_assessment', 'low').lower()
    confidence = result.get('overall_confidence', result.get('confidence', 0))
    
    # Main compliance status
    if result['needs_geo_logic'] is True:
        status_emoji = "🚨"
        status_text = "GEO-SPECIFIC COMPLIANCE REQUIRED"
        st.error(f"{status_emoji} {status_text}")
    elif result['needs_geo_logic'] is False:
        status_emoji = "✅"
        status_text = "NO GEO-SPECIFIC COMPLIANCE DETECTED"
        st.success(f"{status_emoji} {status_text}")
    else:
        status_emoji = "❓"
        status_text = "MANUAL REVIEW REQUIRED"
        st.warning(f"{status_emoji} {status_text}")
    
    # Display detailed confidence breakdown first
    display_detailed_confidence_breakdown(result)
    
    # Display enhanced threshold system results (NEW)
    display_enhanced_threshold_results(result)
    
    # Display comprehensive threshold overview
    display_all_threshold_values(result)
    
    st.markdown("---")
    
    # Create audit-ready display container
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Feature Information Section
    st.subheader("📋 Feature Analysis")
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("**Feature:**")
            st.markdown("**Description:**")
            st.markdown("**Overall Confidence:**")
            st.markdown("**Risk Assessment:**")
            st.markdown("**Legal Reasoning:**")
        
        with col2:
            st.markdown(f"*{title}*")
            st.markdown(f"*{description}*")
            
            # Overall confidence with progress bar
            confidence_percentage = confidence * 100 if isinstance(confidence, (int, float)) else 0
            st.markdown(f"{confidence_percentage:.1f}%")
            st.progress(confidence if isinstance(confidence, (int, float)) else 0.0)
            
            # Show threshold comparison if available
            if result.get('applicable_threshold'):
                threshold = result['applicable_threshold']
                threshold_percentage = threshold * 100
                st.markdown(f"**Threshold:** {threshold_percentage:.1f}%")
                
                # Visual threshold indicator
                if confidence >= threshold:
                    st.success(f"✅ Above threshold ({confidence_percentage:.1f}% ≥ {threshold_percentage:.1f}%)")
                else:
                    st.error(f"❌ Below threshold ({confidence_percentage:.1f}% < {threshold_percentage:.1f}%)")
            
            # Risk assessment with appropriate styling
            risk_colors = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡', 
                'low': '🟢',
                'unknown': '⚪'
            }
            risk_emoji = risk_colors.get(risk_assessment, '⚪')
            st.markdown(f"{risk_emoji} **{risk_assessment.upper()}**")
            
            # Legal reasoning
            st.markdown(f"*{result['reasoning']}*")
    
    st.markdown("---")
    
    # Enhanced Threshold System Results (NEW)
    if result.get('categories_detected') or result.get('escalation_rule'):
        st.subheader("🎯 Enhanced Threshold Analysis")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**Categories Detected:**")
            if result.get('categories_detected'):
                for category in result['categories_detected']:
                    st.markdown(f"• {category.replace('_', ' ').title()}")
            else:
                st.markdown("*No specific categories detected*")
            
            if result.get('applicable_threshold'):
                st.markdown(f"**Applicable Threshold:** {result['applicable_threshold']:.2f}")
        
        with col_b:
            if result.get('escalation_rule'):
                escalation_rule = result['escalation_rule']
                if isinstance(escalation_rule, str):
                    rule_display = escalation_rule
                else:
                    rule_display = escalation_rule.value if hasattr(escalation_rule, 'value') else str(escalation_rule)
                
                st.markdown(f"**Escalation Rule:** {rule_display}")
                
                # Color code based on escalation type
                if 'human_review' in rule_display.lower():
                    st.warning("⚠️ Requires Human Review")
                elif 'auto_ok' in rule_display.lower():
                    st.success("✅ Auto-Approved")
                elif 'ignore' in rule_display.lower():
                    st.info("ℹ️ Ignored")
            
            if result.get('escalation_reason'):
                st.markdown(f"**Reason:** {result['escalation_reason']}")
        
        # Show threshold violations if any
        if result.get('threshold_violations'):
            st.markdown("**⚠️ Threshold Violations:**")
            for violation in result['threshold_violations']:
                st.error(f"• {violation}")
    
    st.markdown("---")
    
    # Applicable Regulations Section
    if result.get('applicable_regulations'):
        st.subheader("⚖️ Applicable Regulations")
        for reg in result['applicable_regulations']:
            with st.expander(f"📜 {reg.get('name', 'Unknown Regulation')} - {reg.get('jurisdiction', 'Unknown')}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Jurisdiction:** {reg.get('jurisdiction', 'Not specified')}")
                    st.markdown(f"**Relevance:** {reg.get('relevance', 'Not assessed')}")
                with col_b:
                    st.markdown(f"**Legal Basis:** {reg.get('legal_basis', 'Not specified')}")
                    articles = reg.get('specific_articles', [])
                    if articles:
                        st.markdown(f"**Articles:** {', '.join(articles)}")
    
    # Regulatory Requirements Section
    if result.get('regulatory_requirements'):
        st.subheader("📌 Legal Requirements")
        for i, req in enumerate(result['regulatory_requirements'], 1):
            st.info(f"**{i}.** {req}")
    
    # Evidence Sources Section (for auditability)
    if result.get('evidence_sources'):
        st.subheader("📚 Evidence Sources")
        with st.expander("View Source Documents"):
            for source in result['evidence_sources']:
                st.markdown(f"• {source}")
    
    # Recommended Actions Section
    if result.get('recommended_actions'):
        st.subheader("🎯 Recommended Actions")
        for i, action in enumerate(result['recommended_actions'], 1):
            st.warning(f"**{i}.** {action}")
    
    # Audit Trail Information
    st.subheader("📋 Audit Information")
    col_audit1, col_audit2 = st.columns(2)
    with col_audit1:
        st.markdown(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        st.markdown(f"**System Version:** Production LLM + RAG")
    with col_audit2:
        st.markdown(f"**Confidence Score:** {confidence:.2f}")
        st.markdown(f"**Risk Level:** {risk_assessment.title()}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def enhanced_threshold_mode():
    """Enhanced threshold system with category-specific confidence thresholds"""
    st.header("🎯 Enhanced Threshold System")
    st.markdown("""
    **Category-specific confidence thresholds** for intelligent compliance decisions:
    - **Legal/Compliance**: 0.90 threshold (super strict)
    - **Safety/Health**: 0.85 threshold (strict)  
    - **Business/Analytics**: 0.70 threshold (moderate)
    - **Internal**: 0.60 threshold (low risk)
    """)
    
    # Create tabs for different testing approaches
    tab1, tab2, tab3 = st.tabs(["🧪 Test Your Features", "📊 Threshold Configuration", "📈 Demo Examples"])
    
    with tab1:
        st.subheader("Test Your Own Features")
        st.markdown("Input a feature description and see how the threshold system categorizes it.")
        
        with st.form("threshold_test_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Feature Title", placeholder="e.g., GDPR Age Gate")
                description = st.text_area("Feature Description", 
                    placeholder="e.g., Age verification for EU users under 16 to comply with GDPR Article 8",
                    height=100)
            
            with col2:
                confidence = st.slider("LLM Confidence", 0.0, 1.0, 0.75, 0.01, 
                    help="Simulate the confidence score from your LLM")
                flag = st.selectbox("LLM Flag", 
                    ["NeedsGeoLogic", "NoGeoLogic", "Ambiguous"],
                    help="Simulate the flag from your LLM")
            
            # Rules matched
            rules_input = st.text_input("Rules Matched (comma-separated)", 
                placeholder="e.g., child_protection, data_residency",
                help="Enter rules that were matched, or leave empty for none")
            
            submitted = st.form_submit_button("🧠 Analyze with Threshold System", type="primary")
            
            if submitted and title and description:
                # Process rules
                rules_matched = [r.strip() for r in rules_input.split(",")] if rules_input else []
                
                # Simulate LLM output
                llm_output = {
                    "flag": flag,
                    "confidence": confidence,
                    "reasoning": f"Simulated output for: {title}",
                    "suggested_jurisdictions": [],
                    "evidence_passage_ids": []
                }
                
                # Import and run the enhanced decision engine
                engine = import_backend_decision_engine()
                if engine:
                    
                    result = engine.make_decision(
                        feature_text=f"{title}: {description}",
                        llm_output=llm_output,
                        rules_matched=rules_matched,
                        rule_fired=len(rules_matched) > 0
                    )
                    
                    # Display results
                    st.success("✅ Analysis Complete!")
                    
                    # Results in columns
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.subheader("📋 Feature Details")
                        st.write(f"**Title:** {title}")
                        st.write(f"**Description:** {description}")
                        st.write(f"**LLM Flag:** {flag}")
                        st.write(f"**LLM Confidence:** {confidence:.2f}")
                        st.write(f"**Rules Matched:** {rules_matched if rules_matched else 'None'}")
                    
                    with col_b:
                        st.subheader("🎯 Category Analysis")
                        st.write(f"**Categories Detected:** {', '.join(result.categories_detected) if result.categories_detected else 'None'}")
                        
                        if result.categories_detected:
                            threshold, escalation = engine.get_applicable_threshold(result.categories_detected)
                            st.write(f"**Applicable Threshold:** {threshold:.2f}")
                            st.write(f"**Escalation Rule:** {escalation.value}")
                    
                    # Final decision
                    st.subheader("📋 Final Decision")
                    
                    # Color-coded result
                    if result.final_flag == "NeedsGeoLogic":
                        st.error(f"🚨 **Final Flag:** {result.final_flag}")
                    elif result.final_flag == "NoGeoLogic":
                        st.success(f"✅ **Final Flag:** {result.final_flag}")
                    else:
                        st.warning(f"⚠️ **Final Flag:** {result.final_flag}")
                    
                    st.write(f"**Final Confidence:** {result.confidence:.2f}")
                    st.write(f"**Review Required:** {result.review_required}")
                    st.write(f"**Review Priority:** {result.review_priority}")
                    
                    if result.escalation_required:
                        st.warning("⚠️ **Escalation Required**")
                        st.write(f"**Reason:** {result.escalation_reason}")
                        if result.threshold_violations:
                            st.write("**Threshold Violations:**")
                            for violation in result.threshold_violations:
                                st.write(f"  • {violation}")
                else:
                    st.error("❌ Could not load the decision engine. Please check the logs above.")
    
    with tab2:
        st.subheader("Threshold Configuration")
        st.markdown("View and understand the category-specific thresholds used by the system.")
        
        engine = import_backend_decision_engine()
        if engine:
            summary = engine.get_threshold_summary()
            
            # Display thresholds in a nice format
            for category, config in summary.items():
                with st.expander(f"📊 {category.replace('_', ' ').title()}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Threshold", f"{config['threshold']:.2f}")
                    with col2:
                        st.metric("Escalation", config['escalation'])
                    with col3:
                        st.metric("Risk Level", 
                            "High" if config['threshold'] >= 0.85 else 
                            "Medium" if config['threshold'] >= 0.70 else "Low")
                    
                    # Load full config for description
                    import json
                    with open("threshold_config.json", "r") as f:
                        full_config = json.load(f)
                    
                    if category in full_config["thresholds"]:
                        st.write(f"**Description:** {full_config['thresholds'][category]['description']}")
                        st.write(f"**Examples:** {', '.join(full_config['thresholds'][category]['examples'])}")
            
        else:
            st.error("❌ Could not load threshold configuration. Please check the logs above.")
    
    with tab3:
        st.subheader("Demo Examples")
        st.markdown("See how different feature types are handled by the threshold system.")
        
        if st.button("🚀 Run Demo Examples"):
            try:
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
                from threshold_demo import run_threshold_demo
                
                # Capture demo output
                import io
                import sys
                
                # Redirect stdout to capture demo output
                old_stdout = sys.stdout
                new_stdout = io.StringIO()
                sys.stdout = new_stdout
                
                try:
                    run_threshold_demo()
                    demo_output = new_stdout.getvalue()
                finally:
                    sys.stdout = old_stdout
                
                # Display demo output
                st.code(demo_output, language="text")
                
            except Exception as e:
                st.error(f"❌ Error running demo: {e}")
                st.info("💡 Make sure threshold_demo.py is in the project root")

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>LoGeo</h1>
        <h2>🌍 Geo-Compliance Detection System</h2>
        <p>Automated compliance detection with enhanced category-specific thresholds using LLMs + RAG</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📋 Navigation")
    mode = st.sidebar.selectbox(
        "Choose Mode:",
        ["Single Feature Analysis", "Batch CSV Processing", "Regulatory Coverage"]
    )
    
    if mode == "Single Feature Analysis":
        single_feature_mode()
    elif mode == "Batch CSV Processing":
        batch_processing_mode()
    elif mode == "Regulatory Coverage":
        regulatory_coverage_mode()

def geo_access_mode():
    """Geo-compliance access control interface"""
    st.header("🌍 Geo-Access Control")
    
    st.markdown("""
    Test geographic access control for different features and countries.
    This uses the new geo-compliance system with Supabase integration.
    """)
    
    with st.form("geo_access_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            user_id = st.text_input("User ID", placeholder="user123")
        with col2:
            feature_name = st.text_input("Feature Name", placeholder="user_registration")
        with col3:
            country = st.text_input("Country Code", placeholder="US")
        
        submitted = st.form_submit_button("🔍 Check Access", type="primary")
        
        if submitted and user_id and feature_name and country:
            with st.spinner("Checking geo-compliance rules..."):
                data = {
                    "user_id": user_id,
                    "feature_name": feature_name,
                    "country": country
                }
                
                response = call_api("/check_access", data=data)
                if response and response.status_code == 200:
                    result = response.json()
                    
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    
                    if result['access_granted']:
                        st.success(f"✅ **Access Granted**")
                        st.info(f"**Reason:** {result['reason']}")
                    else:
                        st.error(f"❌ **Access Denied**")
                        st.warning(f"**Reason:** {result['reason']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show recent access logs
    st.subheader("📊 Recent Access Logs")
    
    if st.button("🔄 Refresh Logs"):
        with st.spinner("Loading access logs..."):
            response = call_api("/logs?limit=10")
            if response and response.status_code == 200:
                logs_data = response.json()
                logs = logs_data.get('logs', [])
                
                if logs:
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    for log in logs:
                        status_icon = "✅" if log['access_granted'] else "❌"
                        st.write(f"{status_icon} **{log['feature_name']}** - User: {log['user_id']} - Country: {log['country']} - {log['timestamp']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("No access logs found.")

def compliance_audit_mode():
    """Compliance audit interface for regulatory analysis results"""
    st.header("📋 Compliance Audit Trail")
    
    st.markdown("""
    **Audit-ready compliance analysis records** for regulatory reporting and legal review.
    All analyses include evidence sources and recommended actions for full traceability.
    """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        limit = st.slider("Number of audit records to show", 10, 100, 25)
    
    with col2:
        if st.button("🔄 Refresh Audit Data"):
            st.rerun()
    
    with st.spinner("Loading compliance audit records..."):
        response = call_api(f"/compliance_audit?limit={limit}")
        if response and response.status_code == 200:
            data = response.json()
            records = data.get('audit_records', [])
            
            if records:
                st.success(f"📈 Found {len(records)} audit records")
                
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                
                for i, record in enumerate(records):
                    # Parse applicable regulations if it's JSON string
                    applicable_regs = record.get('applicable_regulations', [])
                    if isinstance(applicable_regs, str):
                        try:
                            applicable_regs = json.loads(applicable_regs)
                        except:
                            applicable_regs = []
                    
                    with st.expander(f"📋 {record.get('title', 'Untitled Feature')} - {record.get('timestamp', 'No timestamp')[:19]}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**📝 Feature:** {record.get('title', 'N/A')}")
                            st.markdown(f"**📄 Description:** {record.get('description', 'N/A')[:200]}{'...' if len(record.get('description', '')) > 200 else ''}")
                            st.markdown(f"**⚖️ Geo-Compliance Required:** {'🚨 Yes' if record.get('needs_geo_logic') else '✅ No'}")
                            st.markdown(f"**🎯 Confidence:** {record.get('confidence', 0):.2f}")
                        
                        with col2:
                            risk_level = record.get('risk_assessment', 'unknown').lower()
                            risk_icon = "🔴" if risk_level == "critical" else "🟠" if risk_level == "high" else "🟡" if risk_level == "medium" else "🟢"
                            st.markdown(f"**📊 Risk Assessment:** {risk_icon} {record.get('risk_assessment', 'N/A').title()}")
                            
                            if applicable_regs:
                                st.markdown("**⚖️ Applicable Regulations:**")
                                for reg in applicable_regs[:3]:  # Show first 3
                                    if isinstance(reg, dict):
                                        st.markdown(f"• {reg.get('name', 'Unknown')} ({reg.get('jurisdiction', 'Unknown')})")
                                    else:
                                        st.markdown(f"• {reg}")
                            else:
                                st.markdown("**⚖️ Regulations:** None detected")
                        
                        # Legal reasoning
                        st.markdown(f"**💭 Legal Reasoning:** {record.get('reasoning', 'N/A')}")
                        
                        # Evidence sources (critical for audit)
                        evidence = record.get('evidence_sources', '')
                        if evidence and evidence != 'No relevant regulatory documents found':
                            if isinstance(evidence, str) and ';' in evidence:
                                sources = evidence.split(';')
                                st.markdown("**📚 Evidence Sources:**")
                                for source in sources[:3]:  # Show first 3 sources
                                    st.markdown(f"• {source.strip()}")
                        
                        # Recommended actions
                        actions = record.get('recommended_actions', '')
                        if actions:
                            if isinstance(actions, str) and ';' in actions:
                                action_list = actions.split(';')
                                st.markdown("**🎯 Recommended Actions:**")
                                for action in action_list[:2]:  # Show first 2 actions
                                    st.markdown(f"• {action.strip()}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            else:
                st.info("📝 No audit records found. Run some compliance analyses first!")
                st.markdown("""
                💡 **Tip:** Use "Single Feature Analysis" or "Batch CSV Processing" to generate 
                audit records that will appear here for regulatory reporting.
                """)
        else:
            st.error("❌ Failed to load audit records")
            st.info("Make sure your backend is running and properly configured.")

def regulatory_coverage_mode():
    """Display regulatory coverage and document information"""
    st.header("📚 Regulatory Coverage")
    
    st.markdown("""
    **Legitimate regulatory sources** loaded in the system for compliance analysis.
    This shows the coverage of legal documents used for feature analysis.
    """)
    
    if st.button("🔄 Refresh Coverage Data"):
        st.rerun()
    
    with st.spinner("Loading regulatory coverage information..."):
        response = call_api("/regulatory_coverage")
        if response and response.status_code == 200:
            data = response.json()
            
            # Regulation details
            st.subheader("📋 Loaded Regulatory Documents")
            
            regulations = data.get('regulations', [])
            if regulations:
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                
                # Jurisdiction mapping for better display
                jurisdiction_map = {
                    'ca': '🇨🇦 Canada',
                    'eu': '🇪🇺 European Union', 
                    'us': '🇺🇸 United States',
                    'fl': '🇺🇸 Florida, USA',
                    'ut': '🇺🇸 Utah, USA',
                    'ccpa': '🇺🇸 California, USA',
                    'coppa': '🇺🇸 United States (Federal)',
                    'gdpr': '🇪🇺 European Union',
                    'ncmec': '🇺🇸 United States (Federal)'
                }
                
                for reg in regulations:
                    reg_name = reg.get('name', 'Unknown Regulation')
                    filename = reg.get('filename', reg_name.lower().replace(' ', '_'))
                    
                    # Extract jurisdiction from filename
                    jurisdiction = "🌍 Multi-jurisdictional"
                    for prefix, jur in jurisdiction_map.items():
                        if filename.lower().startswith(prefix) or prefix in filename.lower():
                            jurisdiction = jur
                            break
                    
                    # Determine regulation type
                    reg_type = "📋 General Compliance"
                    if any(keyword in reg_name.lower() for keyword in ['child', 'minor', 'kid', 'coppa']):
                        reg_type = "👶 Child Protection"
                    elif any(keyword in reg_name.lower() for keyword in ['data', 'privacy', 'gdpr', 'ccpa']):
                        reg_type = "🔒 Data Privacy"
                    elif any(keyword in reg_name.lower() for keyword in ['dsa', 'platform', 'social']):
                        reg_type = "📱 Platform Regulation"
                    elif any(keyword in reg_name.lower() for keyword in ['reporting', 'ncmec']):
                        reg_type = "📊 Reporting Requirements"
                        
                    with st.expander(f"📜 {reg_name}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"**📍 Jurisdiction:** {jurisdiction}")
                            st.markdown(f"**📊 Content Length:** {reg.get('content_length', 0):,} characters")
                            st.markdown(f"**📋 Type:** {reg_type}")
                        with col_b:
                            # More descriptive status
                            if reg.get('content_length', 0) > 0:
                                status = "✅ Active & Indexed"
                                status_color = "success"
                            else:
                                status = "⚠️ Loaded but Empty"
                                status_color = "warning"
                            
                            st.markdown(f"**🔧 Status:** {status}")
                            
                            # Show content summary
                            content_length = reg.get('content_length', 0)
                            if content_length > 10000:
                                size_desc = "📚 Comprehensive Document"
                            elif content_length > 5000:
                                size_desc = "📄 Standard Document"
                            elif content_length > 1000:
                                size_desc = "📃 Brief Document"
                            else:
                                size_desc = "📝 Summary Document"
                            
                            st.markdown(f"**📑 Size:** {size_desc}")
                            
                            # Calculate approximate reading time
                            words = content_length // 5  # Rough estimate: 5 chars per word
                            reading_time = max(1, words // 200)  # 200 words per minute
                            st.markdown(f"**⏱️ Reading Time:** ~{reading_time} min")
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ No regulatory documents found")
                st.info("Check the /regulations directory for legal document files")
            
            # Jurisdictions covered - Enhanced display
            st.subheader("🌍 Geographic Coverage")
            if regulations:
                # Extract unique jurisdictions from our enhanced mapping
                jurisdiction_map = {
                    'ca': '🇨🇦 Canada',
                    'eu': '🇪🇺 European Union', 
                    'us': '🇺🇸 United States',
                    'fl': '🇺🇸 Florida, USA',
                    'ut': '🇺🇸 Utah, USA',
                    'ccpa': '🇺🇸 California, USA',
                    'coppa': '🇺🇸 United States (Federal)',
                    'gdpr': '🇪🇺 European Union',
                    'ncmec': '🇺🇸 United States (Federal)'
                }
                
                detected_jurisdictions = set()
                for reg in regulations:
                    filename = reg.get('filename', reg.get('name', '').lower().replace(' ', '_'))
                    for prefix, jur in jurisdiction_map.items():
                        if filename.lower().startswith(prefix) or prefix in filename.lower():
                            detected_jurisdictions.add(jur)
                            break
                
                if detected_jurisdictions:
                    # Group by country for better display
                    countries = {}
                    for jur in detected_jurisdictions:
                        if '🇺🇸' in jur:
                            countries.setdefault('🇺🇸 United States', []).append(jur)
                        elif '🇪🇺' in jur:
                            countries.setdefault('🇪🇺 European Union', []).append(jur)
                        elif '🇨🇦' in jur:
                            countries.setdefault('🇨🇦 Canada', []).append(jur)
                    
                    for country, regions in countries.items():
                        unique_regions = list(set(regions))
                        # Filter out the main country from the regions list
                        specific_regions = [region for region in unique_regions if region != country]
                        
                        if len(specific_regions) == 0:
                            # Only show the country if no specific regions
                            st.success(f"{country}")
                        else:
                            # Show country with specific regions listed underneath
                            st.success(f"{country}")
                            for region in specific_regions:
                                # Extract just the state/region name without country repetition
                                if '🇺🇸' in region:
                                    # For US states, extract just the state name
                                    state_name = region.replace('🇺🇸 ', '').replace(', USA', '').replace(' (Federal)', ' (Federal)')
                                    st.info(f"  • {state_name}")
                                elif '🇪🇺' in region:
                                    # For EU regions, extract region name
                                    region_name = region.replace('🇪🇺 ', '')
                                    st.info(f"  • {region_name}")
                                elif '🇨🇦' in region:
                                    # For Canadian regions, extract region name  
                                    region_name = region.replace('🇨🇦 ', '')
                                    st.info(f"  • {region_name}")
                                else:
                                    st.info(f"  • {region}")
                else:
                    st.warning("⚠️ No jurisdiction information available")
            else:
                st.warning("⚠️ No regulatory documents loaded")
                
        else:
            st.error("❌ Failed to load regulatory coverage data")
            st.info("Make sure your backend is running and regulatory documents are loaded.")

def single_feature_mode():
    """Single feature classification interface"""
    st.header("🔍 Single Feature Analysis")
    
    # Input form
    with st.form("feature_form"):
        title = st.text_input(
            "Feature Title",
            placeholder="e.g., User Age Verification System",
            help="Brief name or title of the feature"
        )
        
        description = st.text_area(
            "Feature Description",
            placeholder="e.g., System to verify user age during registration using government ID validation...",
            height=150,
            help="Detailed description of what the feature does"
        )
        
        submitted = st.form_submit_button("🚀 Analyze Feature", type="primary")
    
    # Process submission
    if submitted:
        if not title.strip() or not description.strip():
            st.error("❌ Please provide both title and description")
            return
        
        with st.spinner("🔄 Analyzing feature for geo-compliance requirements..."):
            response = call_api("/classify_enhanced", {
                "title": title.strip(),
                "description": description.strip()
            })
            
            if response:
                result = response.json()
                display_compliance_analysis(result, title, description)

def batch_processing_mode():
    """Batch CSV processing interface"""
    st.header("📊 Batch CSV Processing")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload CSV File")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type="csv",
            help="CSV must contain title (title/feature_name/name) and description (description/feature_description/desc) columns"
        )
        
        if uploaded_file:
            # Preview uploaded data
            df = pd.read_csv(uploaded_file)
            st.subheader("📋 Data Preview")
            st.dataframe(df.head())
            
            # Validate columns (accept multiple naming conventions)
            title_cols = ['title', 'feature_name', 'name']
            desc_cols = ['description', 'feature_description', 'desc']
            
            has_title = any(col in df.columns for col in title_cols)
            has_desc = any(col in df.columns for col in desc_cols)
            
            if not has_title or not has_desc:
                missing = []
                if not has_title:
                    missing.append("title/feature_name/name")
                if not has_desc:
                    missing.append("description/feature_description/desc")
                st.error(f"❌ Missing required columns: {', '.join(missing)}")
                return
            
            st.success(f"✅ Valid CSV with {len(df)} rows")
            
            # Processing options
            st.subheader("📊 Processing Options")
            
            show_detailed = st.checkbox("Show detailed analysis for each feature", value=False)
            
            if show_detailed:
                feature_count = len(df)
                if feature_count > 20:
                    st.warning(f"⚠️ You have {feature_count} features. Detailed analysis will be shown for ALL of them. This may take significantly longer to load and display.")
                else:
                    st.info(f"ℹ️ Detailed analysis will be shown for all {feature_count} features.")
            
            # Process button
            if st.button("🚀 Process Batch", type="primary"):
                # Get title and description column names
                title_col = next((col for col in title_cols if col in df.columns), None)
                desc_col = next((col for col in desc_cols if col in df.columns), None)
                
                with st.spinner(f"🔄 Processing {len(df)} features using enhanced analysis..."):
                    results = []
                    detailed_results = []
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    
                    for idx, row in df.iterrows():
                        # Update progress
                        progress_bar.progress((idx + 1) / len(df))
                        
                        title = str(row[title_col]).strip()
                        description = str(row[desc_col]).strip()
                        
                        if title and description and title.lower() != 'nan' and description.lower() != 'nan':
                            # Use same logic as single feature analysis
                            response = call_api("/classify_enhanced", {
                                "title": title,
                                "description": description
                            })
                            
                            if response:
                                result = response.json()
                                
                                # Store for CSV export
                                results.append({
                                    'title': title,
                                    'description': description,
                                    'needs_geo_logic': result.get('needs_geo_logic'),
                                    'overall_confidence': result.get('overall_confidence', 0),
                                    'primary_confidence': result.get('primary_confidence', 0),
                                    'secondary_confidence': result.get('secondary_confidence', 0),
                                    'risk_assessment': result.get('risk_assessment', 'unknown'),
                                    'reasoning': result.get('reasoning', ''),
                                    'applicable_regulations': str(result.get('applicable_regulations', [])),
                                    'regulatory_requirements': str(result.get('regulatory_requirements', [])),
                                    'recommended_actions': str(result.get('recommended_actions', []))
                                })
                                
                                # Store detailed results for display
                                if show_detailed:
                                    detailed_results.append({
                                        'title': title,
                                        'description': description,
                                        'result': result
                                    })
                            else:
                                # Handle API error
                                results.append({
                                    'title': title,
                                    'description': description,
                                    'needs_geo_logic': 'error',
                                    'overall_confidence': 0,
                                    'primary_confidence': 0,
                                    'secondary_confidence': 0,
                                    'risk_assessment': 'error',
                                    'reasoning': 'API Error - could not process',
                                    'applicable_regulations': '',
                                    'regulatory_requirements': '',
                                    'recommended_actions': ''
                                })
                    
                    progress_bar.empty()
                    
                    if results:
                        st.success("✅ Batch processing completed!")
                        
                        # Create results DataFrame
                        results_df = pd.DataFrame(results)
                        
                        # Provide download link
                        csv_buffer = io.StringIO()
                        results_df.to_csv(csv_buffer, index=False)
                        
                        st.download_button(
                            label="📥 Download Results CSV",
                            data=csv_buffer.getvalue(),
                            file_name=f"enhanced_classified_features_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                        # Summary statistics
                        st.subheader("📈 Summary Statistics")
                        col_a, col_b, col_c = st.columns(3)
                        
                        # Count results
                        compliant = len(results_df[results_df['needs_geo_logic'] == True])
                        non_compliant = len(results_df[results_df['needs_geo_logic'] == False])
                        uncertain = len(results_df[results_df['needs_geo_logic'].isin(['uncertain', 'error'])])
                        
                        with col_a:
                            st.metric("🚨 Requires Compliance", compliant)
                        with col_b:
                            st.metric("✅ No Compliance Needed", non_compliant)
                        with col_c:
                            st.metric("❓ Uncertain/Error", uncertain)
                        
                        # Show results preview
                        st.subheader("📊 Results Preview")
                        st.dataframe(results_df[['title', 'needs_geo_logic', 'overall_confidence', 'risk_assessment']].head(10))
                        
                        # Show detailed analysis if requested
                        if show_detailed and detailed_results:
                            st.subheader(f"🔍 Detailed Analysis ({len(detailed_results)} features)")
                            
                            # For large numbers of features, use expanders to keep interface manageable
                            if len(detailed_results) > 10:
                                for idx, item in enumerate(detailed_results):
                                    with st.expander(f"📋 Feature {idx + 1}: {item['title']}", expanded=False):
                                        display_compliance_analysis(item['result'], item['title'], item['description'])
                            else:
                                # For smaller numbers, show directly with separators
                                for idx, item in enumerate(detailed_results):
                                    st.markdown(f"---")
                                    st.markdown(f"### Feature {idx + 1}: {item['title']}")
                                    display_compliance_analysis(item['result'], item['title'], item['description'])
                    else:
                        st.error("❌ No valid features could be processed")
    
    with col2:
        # Sample CSV download
        st.subheader("📄 Sample CSV Template")
        
        sample_data = {
            'title': [
                'User Registration System',
                'Content Recommendation Engine',
                'Age Verification Gate',
                'Anonymous Chat Feature',
                'Location-Based Services'
            ],
            'description': [
                'Allow users to create accounts with email verification and profile setup',
                'AI system that recommends content based on user behavior and preferences',
                'System to verify user age before allowing access to age-restricted content',
                'Real-time messaging system that allows users to chat without revealing identity',
                'Features that use GPS location to provide location-specific content and services'
            ]
        }
        
        sample_df = pd.DataFrame(sample_data)
        
        # Show sample
        st.dataframe(sample_df)
        
        # Download sample
        csv_buffer = io.StringIO()
        sample_df.to_csv(csv_buffer, index=False)
        
        st.download_button(
            label="📥 Download Sample CSV",
            data=csv_buffer.getvalue(),
            file_name="sample_features.csv",
            mime="text/csv"
        )

def api_status_mode():
    """API status and health check"""
    st.header("🔧 API Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Backend Health Check")
        
        if st.button("🔄 Check API Status"):
            with st.spinner("Checking API status..."):
                response = call_api("/health")
                
                if response:
                    health_data = response.json()
                    st.success("✅ Backend API is healthy!")
                    st.json(health_data)
                else:
                    st.error("❌ Backend API is not responding")
    
    with col2:
        st.subheader("Setup Instructions")
        
        st.markdown("""
        **To run the backend:**
        ```bash
        # Install dependencies
        pip install -r requirements.txt
        
        # Start FastAPI server
        uvicorn backend.main:app --reload
        ```
        
        **To run this frontend:**
        ```bash
        streamlit run frontend/app.py
        ```
        """)
        
        st.info("💡 Make sure the backend is running on http://localhost:8000 before using the classification features.")

def statistics_mode():
    """Statistics and analytics interface"""
    st.header("📊 Classification Statistics")
    
    if st.button("🔄 Refresh Statistics"):
        with st.spinner("Loading statistics..."):
            response = call_api("/stats")
            
            if response:
                stats = response.json()
                
                # Display key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Classifications", stats['total_classifications'])
                
                with col2:
                    st.metric("Compliance Required", stats['compliance_required'])
                
                with col3:
                    st.metric("No Compliance Needed", stats['no_compliance_needed'])
                
                with col4:
                    st.metric("Average Confidence", f"{stats['average_confidence']:.1%}")
                
                # Risk level breakdown
                st.subheader("📈 Risk Level Distribution")
                risk_data = stats['risk_levels']
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("🟢 Low Risk", risk_data['low'])
                with col_b:
                    st.metric("🟡 Medium Risk", risk_data['medium'])
                with col_c:
                    st.metric("🔴 High Risk", risk_data['high'])
                
                # Compliance rate
                if stats['total_classifications'] > 0:
                    compliance_rate = stats['compliance_required'] / stats['total_classifications']
                    st.subheader("📊 Compliance Rate")
                    st.progress(compliance_rate)
                    st.write(f"**{compliance_rate:.1%}** of features require geo-compliance")
                
                # Show raw data
                with st.expander("📋 Raw Statistics Data"):
                    st.json(stats)
            else:
                st.error("❌ Failed to load statistics")



if __name__ == "__main__":
    main()
