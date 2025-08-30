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
        from backend.enhanced_decision_engine import EnhancedDecisionEngine
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
                
            from backend.enhanced_decision_engine import EnhancedDecisionEngine
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
        <h1>🌍 Geo-Compliance Detection System</h1>
        <p>Automated compliance detection with enhanced category-specific thresholds using LLMs + RAG</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📋 Navigation")
    mode = st.sidebar.selectbox(
        "Choose Mode:",
        ["Single Feature Analysis", "Enhanced Threshold System", "Batch CSV Processing", "Compliance Audit", "Regulatory Coverage", "Statistics", "API Status"]
    )
    
    if mode == "Single Feature Analysis":
        single_feature_mode()
    elif mode == "Enhanced Threshold System":
        enhanced_threshold_mode()
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
