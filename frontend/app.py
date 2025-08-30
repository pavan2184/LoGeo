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
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: white !important;
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

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 Geo-Compliance Detection System</h1>
        <p>Automated compliance detection for product features using LLMs + RAG</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📋 Navigation")
    mode = st.sidebar.selectbox(
        "Choose Mode:",
        ["Single Feature Analysis", "Batch CSV Processing", "Compliance Audit", "Regulatory Coverage", "Statistics", "API Status"]
    )
    
    if mode == "Single Feature Analysis":
        single_feature_mode()
    elif mode == "Batch CSV Processing":
        batch_processing_mode()
    elif mode == "Compliance Audit":
        compliance_audit_mode()
    elif mode == "Regulatory Coverage":
        regulatory_coverage_mode()
    elif mode == "Statistics":
        statistics_mode()
    elif mode == "API Status":
        api_status_mode()

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
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📋 Total Regulations", data.get('total_regulations', 0))
            with col2:
                jurisdictions = data.get('jurisdictions_covered', [])
                st.metric("🌍 Jurisdictions", len(jurisdictions))
            with col3:
                status = data.get('system_status', 'unknown')
                status_icon = "✅" if status == "operational" else "❌"
                st.metric("🔧 System Status", f"{status_icon} {status.title()}")
            
            # Regulation details
            st.subheader("📋 Loaded Regulatory Documents")
            
            regulations = data.get('regulations', [])
            if regulations:
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                
                for reg in regulations:
                    with st.expander(f"📜 {reg.get('name', 'Unknown Regulation')}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"**📍 Jurisdiction:** {reg.get('jurisdiction', 'Not specified')}")
                            st.markdown(f"**📊 Content Length:** {reg.get('content_length', 0):,} characters")
                        with col_b:
                            st.markdown(f"**📅 Last Updated:** {reg.get('last_updated', 'Unknown')}")
                            st.markdown(f"**🔧 Status:** Loaded and indexed")
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ No regulatory documents found")
                st.info("Check the /regulations directory for legal document files")
            
            # Jurisdictions covered
            st.subheader("🌍 Geographic Coverage")
            if jurisdictions:
                for jurisdiction in jurisdictions:
                    st.success(f"✅ {jurisdiction}")
            else:
                st.warning("⚠️ No jurisdiction information available")
                
        else:
            st.error("❌ Failed to load regulatory coverage data")
            st.info("Make sure your backend is running and regulatory documents are loaded.")

def single_feature_mode():
    """Single feature classification interface"""
    st.header("🔍 Single Feature Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
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
    
    with col2:
        # Example features sidebar
        st.subheader("💡 Example Features")
        
        examples = [
            {
                "title": "User Age Verification",
                "description": "System to verify user age during registration using government ID validation for compliance with minor protection laws."
            },
            {
                "title": "Content Recommendation Algorithm",
                "description": "AI-powered system that suggests personalized content to users based on their viewing history and preferences."
            },
            {
                "title": "Simple Calculator Widget",
                "description": "Basic arithmetic calculator that performs mathematical operations without storing user data."
            }
        ]
        
        for i, example in enumerate(examples):
            with st.expander(f"Example {i+1}: {example['title']}"):
                st.write(f"**Description:** {example['description']}")
                if st.button(f"Use Example {i+1}", key=f"example_{i}"):
                    st.session_state.example_title = example['title']
                    st.session_state.example_description = example['description']
                    st.rerun()

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
            help="CSV must contain 'title' and 'description' columns"
        )
        
        if uploaded_file:
            # Preview uploaded data
            df = pd.read_csv(uploaded_file)
            st.subheader("📋 Data Preview")
            st.dataframe(df.head())
            
            # Validate columns
            required_cols = ['title', 'description']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                return
            
            st.success(f"✅ Valid CSV with {len(df)} rows")
            
            # Process button
            if st.button("🚀 Process Batch", type="primary"):
                with st.spinner(f"🔄 Processing {len(df)} features..."):
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Send to API
                    response = call_api("/batch_classify", files={
                        "file": ("features.csv", uploaded_file, "text/csv")
                    })
                    
                    if response:
                        # Create download
                        st.success("✅ Batch processing completed!")
                        
                        # Provide download link
                        st.download_button(
                            label="📥 Download Results CSV",
                            data=response.content,
                            file_name=f"classified_features_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                        # Show preview of results
                        result_df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
                        st.subheader("📊 Results Preview")
                        st.dataframe(result_df.head())
                        
                        # Summary statistics
                        if 'needs_geo_logic' in result_df.columns:
                            st.subheader("📈 Summary Statistics")
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                compliant = len(result_df[result_df['needs_geo_logic'] == True])
                                st.metric("⚠️ Requires Compliance", compliant)
                            
                            with col_b:
                                non_compliant = len(result_df[result_df['needs_geo_logic'] == False])
                                st.metric("✅ No Compliance Needed", non_compliant)
                            
                            with col_c:
                                uncertain = len(result_df[result_df['needs_geo_logic'] == 'uncertain'])
                                st.metric("❓ Uncertain", uncertain)
    
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

# Handle example selection from session state
if 'example_title' in st.session_state:
    st.session_state.pop('example_title')
    st.session_state.pop('example_description')

if __name__ == "__main__":
    main()
