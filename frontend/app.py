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
        
        # Add authentication header if available
        if headers is None:
            headers = {}
        if 'access_token' in st.session_state:
            headers['Authorization'] = f"Bearer {st.session_state.access_token}"
        
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

def login_user(username: str, password: str):
    """Login user and get access token"""
    try:
        data = {
            'username': username,
            'password': password
        }
        response = requests.post(f"{API_BASE_URL}/token", data=data)
        response.raise_for_status()
        token_data = response.json()
        st.session_state.access_token = token_data['access_token']
        st.session_state.username = username
        return True
    except Exception as e:
        st.error(f"❌ Login failed: {e}")
        return False

def logout_user():
    """Logout user"""
    if 'access_token' in st.session_state:
        del st.session_state.access_token
    if 'username' in st.session_state:
        del st.session_state.username

def display_classification_result(result: dict, title: str, description: str):
    """Display a single classification result with enhanced UI using Streamlit components"""
    
    # Determine status info and risk level styling
    risk_level = result.get('risk_level', 'low').lower()
    confidence = result.get('confidence', 0)
    
    if result['needs_geo_logic'] is True:
        status_emoji = "⚠️"
        status_text = "GEO-COMPLIANCE REQUIRED"
        st.error(f"{status_emoji} {status_text}")
    elif result['needs_geo_logic'] is False:
        status_emoji = "✅"
        status_text = "NO GEO-COMPLIANCE NEEDED"
        st.success(f"{status_emoji} {status_text}")
    else:  # uncertain
        status_emoji = "❓"
        status_text = "UNCERTAIN - NEEDS REVIEW"
        st.warning(f"{status_emoji} {status_text}")
    
    # Create a white container for the results with dark text
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Create a clean container with better styling
    with st.container():
        # Feature details in a clean format
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("**Feature:**")
            st.markdown("**Description:**")
            st.markdown("**Confidence:**")
            st.markdown("**Risk Level:**")
            st.markdown("**Reasoning:**")
        
        with col2:
            st.markdown(title)
            st.markdown(description)
            
            # Confidence with progress bar
            confidence_percentage = confidence * 100 if isinstance(confidence, (int, float)) else 0
            st.markdown(f"{confidence_percentage:.1f}%")
            st.progress(confidence if isinstance(confidence, (int, float)) else 0.0)
            
            # Risk level with colored badge
            risk_colors = {
                'high': '🔴',
                'medium': '🟡', 
                'low': '🟢'
            }
            risk_emoji = risk_colors.get(risk_level, '🟢')
            st.markdown(f"{risk_emoji} **{risk_level.upper()}**")
            
            st.markdown(result['reasoning'])
    
    st.markdown("---")
    
    # Display regulations using Streamlit components
    if result['regulations']:
        st.subheader("📋 Applicable Regulations")
        for reg in result['regulations']:
            st.info(f"📜 {reg}")
    
    # Display requirements using Streamlit components
    if result.get('specific_requirements'):
        st.subheader("✅ Specific Requirements")
        for req in result['specific_requirements']:
            st.info(f"🔸 {req}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 Geo-Compliance Detection System</h1>
        <p>Automated compliance detection for product features using LLMs + RAG</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication check
    if 'access_token' not in st.session_state:
        login_mode()
        return
    
    # User info in sidebar
    st.sidebar.success(f"👤 Logged in as: {st.session_state.username}")
    if st.sidebar.button("🚪 Logout"):
        logout_user()
        st.rerun()
    
    # Sidebar
    st.sidebar.title("📋 Navigation")
    mode = st.sidebar.selectbox(
        "Choose Mode:",
        ["Single Feature Analysis", "Batch CSV Processing", "Statistics", "API Status"]
    )
    
    if mode == "Single Feature Analysis":
        single_feature_mode()
    elif mode == "Batch CSV Processing":
        batch_processing_mode()
    elif mode == "Statistics":
        statistics_mode()
    elif mode == "API Status":
        api_status_mode()

def login_mode():
    """Login interface"""
    st.header("🔐 Login Required")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="admin or user")
        password = st.text_input("Password", type="password", placeholder="admin123 or user123")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("🔑 Login", type="primary")
        with col2:
            if st.form_submit_button("💡 Demo Credentials"):
                st.info("""
                **Demo Credentials:**
                - Username: `admin`, Password: `admin123`
                - Username: `user`, Password: `user123`
                """)
        
        if submitted:
            if login_user(username, password):
                st.success("✅ Login successful!")
                st.rerun()

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
                response = call_api("/classify", {
                    "title": title.strip(),
                    "description": description.strip()
                })
                
                if response:
                    result = response.json()
                    display_classification_result(result, title, description)
    
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
