"""
Tests for Healthcare CDSS State Management
"""

import pytest
from datetime import datetime
from src.state.healthcare_state import (
    PatientInfo,
    Symptom,
    ClinicalState,
    create_initial_state,
    add_safety_alert,
    add_todo
)


class TestPatientInfo:
    """Tests for PatientInfo model"""
    
    def test_create_valid_patient(self):
        """Test creating valid patient info"""
        patient = PatientInfo(
            patient_id="P001",
            age=45,
            sex="M",
            weight_kg=75.0,
            height_cm=175.0,
            allergies=["Penicillin"],
            current_medications=["Lisinopril"],
            chronic_conditions=["Hypertension"]
        )
        
        assert patient.patient_id == "P001"
        assert patient.age == 45
        assert patient.sex == "M"
    
    def test_bmi_calculation(self):
        """Test BMI calculation"""
        patient = PatientInfo(
            patient_id="P001",
            age=30,
            sex="F",
            weight_kg=70.0,
            height_cm=170.0,
            allergies=[],
            current_medications=[],
            chronic_conditions=[]
        )
        
        bmi = patient.get_bmi()
        assert 24.0 <= bmi <= 25.0  # 70 / (1.7^2) ≈ 24.22
    
    def test_pediatric_check(self):
        """Test pediatric patient detection"""
        child = PatientInfo(
            patient_id="P002",
            age=12,
            sex="M",
            weight_kg=40.0,
            height_cm=150.0,
            allergies=[],
            current_medications=[],
            chronic_conditions=[]
        )
        
        assert child.is_pediatric() == True
        assert child.is_geriatric() == False
    
    def test_geriatric_check(self):
        """Test geriatric patient detection"""
        elder = PatientInfo(
            patient_id="P003",
            age=75,
            sex="F",
            weight_kg=60.0,
            height_cm=160.0,
            allergies=[],
            current_medications=[],
            chronic_conditions=[]
        )
        
        assert elder.is_pediatric() == False
        assert elder.is_geriatric() == True


class TestSymptom:
    """Tests for Symptom model"""
    
    def test_create_symptom(self):
        """Test creating a symptom"""
        symptom = Symptom(
            description="fever",
            severity="moderate",
            onset="2 days ago",
            duration="ongoing"
        )
        
        assert symptom.description == "fever"
        assert symptom.severity == "moderate"
        assert symptom.is_severe() == False
    
    def test_severe_symptom(self):
        """Test severe symptom detection"""
        symptom = Symptom(
            description="chest pain",
            severity="severe",
            onset="1 hour ago",
            duration="ongoing"
        )
        
        assert symptom.is_severe() == True


class TestClinicalState:
    """Tests for clinical state management"""
    
    def test_create_initial_state(self):
        """Test creating initial clinical state"""
        patient = PatientInfo(
            patient_id="P001",
            age=40,
            sex="M",
            weight_kg=80.0,
            height_cm=180.0,
            allergies=[],
            current_medications=[],
            chronic_conditions=[]
        )
        
        symptoms = [
            Symptom(
                description="headache",
                severity="mild",
                onset="today",
                duration="2 hours"
            )
        ]
        
        state = create_initial_state(
            patient_info=patient,
            chief_complaint="Headache",
            symptoms=symptoms,
            vital_signs={"temperature": 37.0}
        )
        
        assert state["patient_info"] == patient
        assert state["chief_complaint"] == "Headache"
        assert len(state["symptoms"]) == 1
        assert state["requires_human_review"] == False
        assert len(state["todos"]) == 0
    
    def test_add_safety_alert(self):
        """Test adding safety alert to state"""
        state = create_initial_state(
            patient_info=PatientInfo(
                patient_id="P001",
                age=25,
                sex="F",
                weight_kg=60.0,
                height_cm=165.0,
                allergies=[],
                current_medications=[],
                chronic_conditions=[]
            ),
            chief_complaint="Test",
            symptoms=[],
            vital_signs={}
        )
        
        updated_state = add_safety_alert(
            state,
            "Test alert",
            require_review=True
        )
        
        assert len(updated_state["safety_alerts"]) == 1
        assert updated_state["requires_human_review"] == True
        assert len(updated_state["review_reasons"]) == 1
    
    def test_add_todo(self):
        """Test adding TODO to state"""
        state = create_initial_state(
            patient_info=PatientInfo(
                patient_id="P001",
                age=25,
                sex="F",
                weight_kg=60.0,
                height_cm=165.0,
                allergies=[],
                current_medications=[],
                chronic_conditions=[]
            ),
            chief_complaint="Test",
            symptoms=[],
            vital_signs={}
        )
        
        updated_state = add_todo(
            state,
            "Perform symptom analysis",
            priority="high"
        )
        
        assert len(updated_state["todos"]) == 1
        assert updated_state["todos"][0]["content"] == "Perform symptom analysis"
        assert updated_state["todos"][0]["priority"] == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
