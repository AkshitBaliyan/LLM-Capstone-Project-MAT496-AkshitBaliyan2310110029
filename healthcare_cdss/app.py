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
from examples import get_all_demo_cases


# Page configuration
st.set_page_config(
    page_title="Healthcare CDSS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .diagnosis-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">🏥 Healthcare Clinical Decision Support System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Clinical Analysis with LangGraph</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Input mode selection
        input_mode = st.radio(
            "Input Mode",
            ["Use Demo Case", "Manual Input"],
            help="Choose between pre-loaded demo cases or manual patient entry"
        )
        
        st.markdown("---")
        
        if input_mode == "Use Demo Case":
            demo_case = st.selectbox(
                "Select Demo Case",
                ["URI (Routine)", "Cardiac Emergency", "Pediatric", "Geriatric"],
                help="Pre-loaded clinical scenarios for demonstration"
            )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This CDSS uses:
        - **LangGraph** for workflow
        - **Claude Sonnet 4** for analysis
        - **PubMed** for evidence
        - **LangSmith** for tracing
        """)
    
    # Main content area
    if input_mode == "Use Demo Case":
        run_demo_case(demo_case)
    else:
        run_manual_input()


def run_demo_case(case_name):
    """Run analysis on a demo case"""
    
    st.header(f"📋 Demo Case: {case_name}")
    
    # Load demo case
    cases = get_all_demo_cases()
    case_map = {
        "URI (Routine)": "uri",
        "Cardiac Emergency": "cardiac_emergency",
        "Pediatric": "pediatric",
        "Geriatric": "geriatric"
    }
    
    state = cases[case_map[case_name]]
    
    # Display patient info
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Patient Information")
        patient = state["patient_info"]
        st.write(f"**Age:** {patient.age} years")
        st.write(f"**Sex:** {patient.sex}")
        st.write(f"**BMI:** {patient.get_bmi():.1f}")
        st.write(f"**Allergies:** {', '.join(patient.allergies) if patient.allergies else 'None'}")
       
        if patient.chronic_conditions:
            st.write(f"**Chronic Conditions:** {', '.join(patient.chronic_conditions)}")
    
    with col2:
        st.subheader("Presenting Symptoms")
        st.write(f"**Chief Complaint:** {state['chief_complaint']}")
        
        for symptom in state["symptoms"]:
            st.write(f"- {symptom.description.title()}: {symptom.severity} severity")
    
    # Run analysis button
    if st.button("🔬 Run Clinical Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing patient case... This may take 20-30 seconds"):
            try:
                result = run_clinical_analysis(state)
                display_results(result)
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)


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
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("❌ ANTHROPIC_API_KEY not found in environment variables")
        st.info("Please create a .env file with your API keys. See .env.example for template.")
        st.stop()
    
    main()
