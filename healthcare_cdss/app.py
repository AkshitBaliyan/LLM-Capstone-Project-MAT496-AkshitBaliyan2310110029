"""
Streamlit Web UI for Healthcare CDSS

A user-friendly web interface for the Clinical Decision Support System.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.state import PatientInfo, Symptom, create_initial_state
from src.agents import run_clinical_analysis


# Page configuration
st.set_page_config(
    page_title="Healthcare CDSS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar since we don't use it
)

# Custom CSS - Enhanced Modern Design
st.markdown("""
<style>
    /* Main header with gradient */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeIn 1s ease-in;
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: #718096;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Diagnosis cards with hover effect */
    .diagnosis-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .diagnosis-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.1);
    }
    
    /* Alert box with better styling */
    .alert-box {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 5px solid #ef4444;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(239,68,68,0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Button enhancements */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102,126,234,0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(102,126,234,0.4);
    }
    
    /* Card containers */
    .stExpander {
        background: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Progress indicators */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }
    
    /* Better spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">🏥 Healthcare Clinical Decision Support System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Clinical Analysis with LangGraph</div>', unsafe_allow_html=True)
    
    # Directly show manual input form
    run_manual_input()


def run_manual_input():
    """Run analysis with manual patient input"""
    
    st.header("📝 Manual Patient Entry")
    
    # Patient Information
    st.subheader("Patient Demographics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=45)
        sex = st.selectbox("Sex", ["M", "F", "Other"])
    
    with col2:
        weight_kg = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=75.0)
        height_cm = st.number_input("Height (cm)", min_value=30.0, max_value=250.0, value=170.0)
    
    with col3:
        allergies = st.text_area("Allergies (one per line)", help="Enter known allergies, one per line")
        medications = st.text_area("Current Medications", help="Enter current medications, one per line")
    
    # Chief Complaint
    st.subheader("Chief Complaint")
    chief_complaint = st.text_input("Main reason for visit", placeholder="e.g., Fever and cough for 3 days")
    
    # Symptoms
    st.subheader("Symptoms")
    
    num_symptoms = st.number_input("Number of symptoms", min_value=1, max_value=10, value=2)
    
    symptoms = []
    cols = st.columns(2)
    
    for i in range(num_symptoms):
        col_idx = i % 2
        with cols[col_idx]:
            st.markdown(f"**Symptom {i+1}**")
            description = st.text_input(f"Description", key=f"desc_{i}", placeholder="e.g., fever")
            severity = st.selectbox(f"Severity", ["mild", "moderate", "severe"], key=f"sev_{i}")
            onset = st.text_input(f"Onset", key=f"onset_{i}", placeholder="e.g., 3 days ago")
            
            if description:
                symptoms.append(Symptom(
                    description=description,
                    severity=severity,
                    onset=onset,
                    duration="ongoing"
                ))
    
    # Vital Signs
    st.subheader("Vital Signs")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temp = st.number_input("Temperature (°C)", min_value=35.0, max_value=42.0, value=37.0, step=0.1)
    with col2:
        hr = st.number_input("Heart Rate", min_value=40, max_value=200, value=75)
    with col3:
        rr = st.number_input("Respiratory Rate", min_value=8, max_value=40, value=16)
    with col4:
        bp_sys = st.number_input("BP Systolic", min_value=70, max_value=200, value=120)
    
    # Run analysis
    if st.button("🔬 Run Clinical Analysis", type="primary", use_container_width=True):
        if not chief_complaint or not symptoms:
            st.warning("⚠️ Please enter chief complaint and at least one symptom")
            return
        
        with st.spinner("Analyzing patient case... This may take 20-30 seconds"):
            try:
                # Create patient
                patient = PatientInfo(
                    patient_id=f"MANUAL_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    age=age,
                    sex=sex,
                    weight_kg=weight_kg,
                    height_cm=height_cm,
                    allergies=[a.strip() for a in allergies.split('\n') if a.strip()],
                    current_medications=[m.strip() for m in medications.split('\n') if m.strip()],
                    chronic_conditions=[]
                )
                
                # Create state
                state = create_initial_state(
                    patient_info=patient,
                    chief_complaint=chief_complaint,
                    symptoms=symptoms,
                    vital_signs={
                        "temperature": temp,
                        "heart_rate": hr,
                        "respiratory_rate": rr,
                        "bp_systolic": bp_sys
                    }
                )
                
                # Run analysis
                result = run_clinical_analysis(state)
                display_results(result)
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)


def display_results(result):
    """Display analysis results"""
    
    st.markdown("---")
    st.header("📊 Clinical Analysis Results")
    
    # Safety Alerts
    if result.get("safety_alerts"):
        st.markdown('<div class="alert-box">', unsafe_allow_html=True)
        st.subheader("🚨 Safety Alerts")
        for alert in result["safety_alerts"]:
            st.warning(alert)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Human Review Required
    if result.get("requires_human_review"):
        st.error("⚕️ **HUMAN REVIEW REQUIRED**")
        for reason in result.get("review_reasons", []):
            st.write(f"- {reason}")
    
    # Differential Diagnosis
    if result.get("differential_diagnosis"):
        st.subheader("🔬 Differential Diagnosis")
        
        for i, dx in enumerate(result["differential_diagnosis"][:5], 1):
            with st.expander(f"{i}. {dx['condition']} ({dx['probability']*100:.1f}% probability)", expanded=(i==1)):
                st.write(f"**Clinical Reasoning:**")
                st.write(dx['reasoning'])
                
                if dx.get('typical_symptoms'):
                    st.write(f"**Typical Symptoms:** {', '.join(dx['typical_symptoms'])}")
                
                if dx.get('red_flags'):
                    st.write(f"**⚠️ Red Flags:** {', '.join(dx['red_flags'])}")
                
                if dx.get('icd10_code'):
                    st.write(f"**ICD-10 Code:** {dx['icd10_code']}")
    
    # Recommended Tests
    if result.get("recommended_tests"):
        st.subheader("🧪 Recommended Diagnostic Tests")
        for test in result["recommended_tests"]:
            st.write(f"- {test}")
    
    # Medical Literature Evidence
    if result.get("evidence_sources"):
        st.subheader("📚 Supporting Medical Evidence")
        for i, source in enumerate(result["evidence_sources"][:3], 1):
            st.write(f"{i}. {source}")
    
    # Session Information
    with st.expander("ℹ️ Session Information"):
        st.write(f"**Session ID:** {result.get('session_id', 'N/A')}")
        st.write(f"**Timestamp:** {result.get('timestamp', 'N/A')}")
        st.write(f"**Version:** {result.get('version', 'N/A')}")
        
        if result.get("confidence_scores"):
            st.write(f"**Confidence Scores:**")
            for key, value in result["confidence_scores"].items():
                st.write(f"  - {key}: {value:.2f}")


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OPENAI_API_KEY not found in environment variables")
        st.info("Please create a .env file with your API keys. See .env.example for template.")
        st.stop()
    
    main()
