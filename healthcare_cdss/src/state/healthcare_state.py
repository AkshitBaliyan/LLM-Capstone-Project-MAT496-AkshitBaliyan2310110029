"""
Healthcare Clinical Decision Support - State Management

This module defines the state schema for the CDSS system, including:
- Patient information
- Symptoms and vital signs
- Analysis results
- Safety alerts and compliance tracking
"""

from typing_extensions import TypedDict
from typing import Annotated, Literal, Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from langgraph.graph import add_messages


class PatientInfo(BaseModel):
    """Structured patient information with validation"""
    
    patient_id: str = Field(..., description="Unique patient identifier")
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    sex: Literal["M", "F", "Other"] = Field(..., description="Biological sex")
    weight_kg: float = Field(..., gt=0, le=500, description="Weight in kilograms")
    height_cm: float = Field(..., gt=0, le=300, description="Height in centimeters")
    allergies: list[str] = Field(default_factory=list, description="Known allergies")
    current_medications: list[str] = Field(
        default_factory=list, 
        description="Currently prescribed medications"
    )
    chronic_conditions: list[str] = Field(
        default_factory=list,
        description="Chronic medical conditions"
    )
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        """Ensure age is reasonable"""
        if v < 0 or v > 120:
            raise ValueError("Age must be between 0 and 120")
        return v
    
    def get_bmi(self) -> float:
        """Calculate BMI"""
        height_m = self.height_cm / 100
        return round(self.weight_kg / (height_m ** 2), 2)
    
    def is_pediatric(self) -> bool:
        """Check if patient is pediatric (<18 years)"""
        return self.age < 18
    
    def is_geriatric(self) -> bool:
        """Check if patient is geriatric (>=65 years)"""
        return self.age >= 65


class Symptom(BaseModel):
    """Structured symptom data with clinical details"""
    
    description: str = Field(..., description="Symptom description")
    severity: Literal["mild", "moderate", "severe"] = Field(
        ..., 
        description="Symptom severity level"
    )
    onset: str = Field(..., description="When symptom started (e.g., '2 days ago')")
    duration: str = Field(..., description="How long symptom has lasted")
    location: Optional[str] = Field(None, description="Body location if applicable")
    characteristics: Optional[str] = Field(
        None, 
        description="Additional characteristics (e.g., 'sharp', 'dull')"
    )
    
    def is_severe(self) -> bool:
        """Check if symptom is severe"""
        return self.severity == "severe"


class Diagnosis(BaseModel):
    """Structured differential diagnosis"""
    
    condition: str = Field(..., description="Medical condition name")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability score 0-1")
    reasoning: str = Field(..., description="Clinical reasoning for this diagnosis")
    typical_symptoms: list[str] = Field(
        default_factory=list,
        description="Symptoms typically associated with this condition"
    )
    red_flags: list[str] = Field(
        default_factory=list,
        description="Warning signs requiring immediate attention"
    )
    icd10_code: Optional[str] = Field(None, description="ICD-10 diagnosis code")


class TreatmentOption(BaseModel):
    """Structured treatment recommendation"""
    
    treatment_type: Literal["medication", "procedure", "lifestyle", "referral"]
    name: str = Field(..., description="Treatment name")
    description: str = Field(..., description="Detailed description")
    dosage: Optional[str] = Field(None, description="Dosage if medication")
    frequency: Optional[str] = Field(None, description="How often to administer")
    duration: Optional[str] = Field(None, description="Treatment duration")
    contraindications: list[str] = Field(
        default_factory=list,
        description="Situations where treatment should not be used"
    )
    evidence_level: Literal["A", "B", "C", "D", "Expert Opinion"] = Field(
        ..., 
        description="Strength of evidence supporting treatment"
    )


class DrugInteraction(BaseModel):
    """Drug interaction details"""
    
    drug1: str = Field(..., description="First drug in interaction")
    drug2: str = Field(..., description="Second drug in interaction")
    severity: Literal["mild", "moderate", "severe", "contraindicated"] = Field(
        ..., 
        description="Interaction severity"
    )
    description: str = Field(..., description="Interaction description")
    management: str = Field(..., description="How to manage this interaction")
    source: str = Field(..., description="Source of interaction data")


class Todo(BaseModel):
    """Clinical analysis task tracking"""
    
    content: str = Field(..., description="Task description")
    status: Literal["pending", "in_progress", "completed"] = Field(
        default="pending",
        description="Task status"
    )
    priority: Literal["low", "medium", "high", "urgent"] = Field(
        default="medium",
        description="Task priority"
    )
    assigned_agent: Optional[str] = Field(None, description="Agent handling this task")


class ClinicalState(TypedDict):
    """
    Main state for Clinical Decision Support System
    
    This state is passed between agents and contains all information
    needed for clinical decision making, safety checks, and tracking.
    """
    
    # ===== INPUT DATA =====
    patient_info: PatientInfo
    chief_complaint: str  # Main reason for visit
    symptoms: list[Symptom]
    vital_signs: dict[str, float]  # e.g., {"temperature": 38.2, "heart_rate": 88}
    
    # ===== AGENT COMMUNICATION =====
    messages: Annotated[list, add_messages]  # LangGraph message history
    
    # ===== CONTEXT MANAGEMENT (from research agent pattern) =====
    files: dict[str, str]  # Virtual file system for storing literature, guidelines
    todos: list[dict]  # Track analysis tasks across agents
    
    # ===== ANALYSIS RESULTS =====
    differential_diagnosis: list[dict]  # List of possible diagnoses
    recommended_tests: list[str]  # Diagnostic tests to order
    treatment_options: list[dict]  # Treatment recommendations
    drug_interactions: list[dict]  # Detected drug interactions
    contraindications: list[str]  # Treatment contraindications
    
    # ===== SAFETY & COMPLIANCE =====
    confidence_scores: dict[str, float]  # Confidence in various analyses
    evidence_sources: list[str]  # Citations for recommendations
    safety_alerts: list[str]  # Critical safety warnings
    requires_human_review: bool  # Flag for mandatory human review
    review_reasons: list[str]  # Why human review is needed
    
    # ===== METADATA =====
    session_id: str  # Unique session identifier
    timestamp: datetime  # When analysis started
    version: str  # CDSS version
    

class EvaluationCase(BaseModel):
    """Structure for clinical evaluation cases"""
    
    case_id: str = Field(..., description="Unique case identifier")
    description: str = Field(..., description="Case description")
    
    # Inputs
    patient_info: PatientInfo
    chief_complaint: str
    symptoms: list[Symptom]
    vital_signs: dict[str, float]
    
    # Expected outputs (ground truth)
    expected_diagnosis: str = Field(..., description="Correct primary diagnosis")
    expected_tests: list[str] = Field(default_factory=list)
    expected_treatments: list[str] = Field(default_factory=list)
    
    # Metadata
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="Case difficulty level"
    )
    specialty: str = Field(default="general", description="Medical specialty")
    notes: Optional[str] = Field(None, description="Additional notes for evaluators")


# Helper functions for state management

def create_initial_state(
    patient_info: PatientInfo,
    chief_complaint: str,
    symptoms: list[Symptom],
    vital_signs: dict[str, float]
) -> ClinicalState:
    """
    Create initial clinical state for a new case
    
    Args:
        patient_info: Patient demographic and medical history
        chief_complaint: Main reason for consultation
        symptoms: List of symptoms patient is experiencing
        vital_signs: Current vital sign measurements
    
    Returns:
        Initialized ClinicalState ready for workflow
    """
    import uuid
    
    return {
        # Input data
        "patient_info": patient_info,
        "chief_complaint": chief_complaint,
        "symptoms": symptoms,
        "vital_signs": vital_signs,
        
        # Agent communication
        "messages": [],
        
        # Context management
        "files": {},
        "todos": [],
        
        # Analysis results (empty initially)
        "differential_diagnosis": [],
        "recommended_tests": [],
        "treatment_options": [],
        "drug_interactions": [],
        "contraindications": [],
        
        # Safety & compliance
        "confidence_scores": {},
        "evidence_sources": [],
        "safety_alerts": [],
        "requires_human_review": False,
        "review_reasons": [],
        
        # Metadata
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.now(),
        "version": "1.0.0-phase1"
    }


def add_safety_alert(state: ClinicalState, alert: str, require_review: bool = True) -> ClinicalState:
    """
    Add a safety alert to the state
    
    Args:
        state: Current clinical state
        alert: Safety alert message
        require_review: Whether to flag for human review
    
    Returns:
        Updated state with safety alert
    """
    state["safety_alerts"].append(alert)
    if require_review:
        state["requires_human_review"] = True
        state["review_reasons"].append(f"Safety alert: {alert}")
    return state


def add_todo(state: ClinicalState, content: str, priority: str = "medium") -> ClinicalState:
    """
    Add a task to the TODO list
    
    Args:
        state: Current clinical state
        content: Task description
        priority: Task priority level
    
    Returns:
        Updated state with new TODO
    """
    todo = {
        "content": content,
        "status": "pending",
        "priority": priority,
        "assigned_agent": None
    }
    state["todos"].append(todo)
    return state
