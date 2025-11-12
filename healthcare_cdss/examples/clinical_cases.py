"""
Example Clinical Cases for Healthcare CDSS

This module contains example patient cases for testing and demonstration.
Each case includes patient information, symptoms, and expected outcomes.
"""

from src.state.healthcare_state import PatientInfo, Symptom, create_initial_state


def get_uri_case():
    """Upper Respiratory Infection - Simple routine case"""
    patient = PatientInfo(
        patient_id="DEMO001",
        age=35,
        sex="M",
        weight_kg=80.0,
        height_cm=175.0,
        allergies=["Penicillin"],
        current_medications=["Lisinopril 10mg daily"],
        chronic_conditions=["Hypertension"]
    )
    
    symptoms = [
        Symptom(
            description="fever",
            severity="moderate",
            onset="3 days ago",
            duration="ongoing"
        ),
        Symptom(
            description="dry cough",
            severity="moderate",
            onset="3 days ago",
            duration="ongoing"
        ),
        Symptom(
            description="fatigue",
            severity="mild",
            onset="2 days ago",
            duration="ongoing"
        )
    ]
    
    return create_initial_state(
        patient_info=patient,
        chief_complaint="Fever and cough for 3 days",
        symptoms=symptoms,
        vital_signs={
            "temperature": 38.2,
            "heart_rate": 88,
            "respiratory_rate": 18,
            "bp_systolic": 135,
            "bp_diastolic": 85
        }
    )


def get_cardiac_emergency_case():
    """Acute Coronary Syndrome - Critical case with red flags"""
    patient = PatientInfo(
        patient_id="DEMO002",
        age=58,
        sex="M",
        weight_kg=95.0,
        height_cm=178.0,
        allergies=[],
        current_medications=["Metformin"],
        chronic_conditions=["Type 2 Diabetes", "Hyperlipidemia"]
    )
    
    symptoms = [
        Symptom(
            description="crushing chest pain",
            severity="severe",
            onset="30 minutes ago",
            duration="ongoing",
            location="chest",
            characteristics="radiating to left arm"
        ),
        Symptom(
            description="shortness of breath",
            severity="moderate",
            onset="30 minutes ago",
            duration="ongoing"
        ),
        Symptom(
            description="nausea",
            severity="mild",
            onset="20 minutes ago",
            duration="ongoing"
        ),
        Symptom(
            description="diaphoresis",
            severity="moderate",
            onset="30 minutes ago",
            duration="ongoing"
        )
    ]
    
    return create_initial_state(
        patient_info=patient,
        chief_complaint="Severe chest pain radiating to left arm",
        symptoms=symptoms,
        vital_signs={
            "temperature": 37.0,
            "heart_rate": 110,
            "respiratory_rate": 22,
            "bp_systolic": 145,
            "bp_diastolic": 95
        }
    )


def get_pediatric_case():
    """Pediatric case - triggers special handling"""
    patient = PatientInfo(
        patient_id="DEMO003",
        age=8,
        sex="F",
        weight_kg=25.0,
        height_cm=130.0,
        allergies=["Eggs"],
        current_medications=[],
        chronic_conditions=["Asthma"]
    )
    
    symptoms = [
        Symptom(
            description="fever",
            severity="moderate",
            onset="1 day ago",
            duration="ongoing"
        ),
        Symptom(
            description="sore throat",
            severity="moderate",
            onset="2 days ago",
            duration="ongoing"
        ),
        Symptom(
            description="difficulty swallowing",
            severity="mild",
            onset="1 day ago",
            duration="ongoing"
        )
    ]
    
    return create_initial_state(
        patient_info=patient,
        chief_complaint="Fever and sore throat",
        symptoms=symptoms,
        vital_signs={
            "temperature": 38.5,
            "heart_rate": 95,
            "respiratory_rate": 20,
            "bp_systolic": 100,
            "bp_diastolic": 65
        }
    )


def get_geriatric_case():
    """Geriatric case with multiple comorbidities"""
    patient = PatientInfo(
        patient_id="DEMO004",
        age=75,
        sex="F",
        weight_kg=65.0,
        height_cm=160.0,
        allergies=["Sulfa drugs"],
        current_medications=[
            "Lisinopril 20mg",
            "Metoprolol 50mg",
            "Atorvastatin 40mg",
            "Aspirin 81mg"
        ],
        chronic_conditions=[
            "Hypertension",
            "Coronary Artery Disease",
            "Hyperlipidemia",
            "Osteoarthritis"
        ]
    )
    
    symptoms = [
        Symptom(
            description="dizziness",
            severity="moderate",
            onset="2 days ago",
            duration="intermittent"
        ),
        Symptom(
            description="fatigue",
            severity="moderate",
            onset="1 week ago",
            duration="ongoing"
        ),
        Symptom(
            description="shortness of breath",
            severity="mild",
            onset="3 days ago",
            duration="with exertion"
        )
    ]
    
    return create_initial_state(
        patient_info=patient,
        chief_complaint="Dizziness and fatigue",
        symptoms=symptoms,
        vital_signs={
            "temperature": 36.8,
            "heart_rate": 58,
            "respiratory_rate": 16,
            "bp_systolic": 95,
            "bp_diastolic": 60
        }
    )


def get_all_demo_cases():
    """Get all demonstration cases"""
    return {
        "uri": get_uri_case(),
        "cardiac_emergency": get_cardiac_emergency_case(),
        "pediatric": get_pediatric_case(),
        "geriatric": get_geriatric_case()
    }
