"""
Symptom Analysis Tools for Healthcare CDSS

This module provides tools for analyzing patient symptoms and generating
differential diagnoses using structured LLM outputs.
"""

from typing import Annotated, List
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field

from ..state.healthcare_state import ClinicalState, Diagnosis


# Initialize LLM for symptom analysis
symptom_analysis_model = init_chat_model(
    "openai:gpt-4o",
    temperature=0.0  # Deterministic for medical analysis
)


class SymptomAnalysisResult(BaseModel):
    """Structured output for symptom analysis"""
    
    diagnoses: List[Diagnosis] = Field(
        description="List of differential diagnoses ordered by probability"
    )
    red_flags: List[str] = Field(
        default_factory=list,
        description="Critical warning signs requiring immediate attention"
    )
    recommended_tests: List[str] = Field(
        default_factory=list,
        description="Diagnostic tests to confirm or rule out conditions"
    )
    clinical_reasoning: str = Field(
        description="Overall clinical reasoning and thought process"
    )
    urgency_level: str = Field(
        description="Triage level: routine, urgent, or emergent"
    )


def create_symptom_analysis_prompt(state: ClinicalState) -> str:
    """
    Create a detailed prompt for symptom analysis
    
    Args:
        state: Current clinical state
    
    Returns:
        Formatted prompt string
    """
    patient = state["patient_info"]
    symptoms = state["symptoms"]
    vitals = state["vital_signs"]
    
    # Format symptoms
    symptom_text = "\n".join([
        f"- {s.description}: {s.severity} severity, onset {s.onset}, duration {s.duration}"
        for s in symptoms
    ])
    
    # Format vital signs
    vitals_text = "\n".join([f"- {k}: {v}" for k, v in vitals.items()])
    
    # Create comprehensive prompt
    prompt = f"""You are an expert clinical decision support system. Analyze the following patient case and provide a differential diagnosis.

PATIENT DEMOGRAPHICS:
- Age: {patient.age} years old
- Sex: {patient.sex}
- BMI: {patient.get_bmi()}

MEDICAL HISTORY:
- Allergies: {', '.join(patient.allergies) if patient.allergies else 'None reported'}
- Current Medications: {', '.join(patient.current_medications) if patient.current_medications else 'None'}
- Chronic Conditions: {', '.join(patient.chronic_conditions) if patient.chronic_conditions else 'None'}

CHIEF COMPLAINT:
{state['chief_complaint']}

PRESENTING SYMPTOMS:
{symptom_text}

VITAL SIGNS:
{vitals_text}

INSTRUCTIONS:
1. Generate a differential diagnosis with 3-5 most likely conditions
2. For each diagnosis:
   - Provide probability estimate (0.0 to 1.0)
   - Explain clinical reasoning
   - List typical symptoms associated with this condition
   - Identify any red flags (warning signs)
3. Consider patient-specific factors (age, sex, chronic conditions)
4. Identify RED FLAGS that require immediate medical attention
5. Recommend appropriate diagnostic tests
6. Determine urgency level (routine, urgent, or emergent)

SPECIAL CONSIDERATIONS:
- Patient is {"pediatric (age < 18)" if patient.is_pediatric() else "geriatric (age >= 65)" if patient.is_geriatric() else "adult"}
- Consider age-appropriate differential diagnoses
- Account for existing chronic conditions and medications
- Flag any life-threatening conditions immediately

Provide a thorough, evidence-based analysis."""

    return prompt


@tool(parse_docstring=True)
def analyze_symptoms_tool(
    state: Annotated[ClinicalState, InjectedState],
    tool_call_id: str = "symptom_analysis"
) -> Command:
    """Analyze patient symptoms and generate differential diagnosis.
    
    This tool performs comprehensive symptom analysis using clinical reasoning
    to generate a prioritized differential diagnosis list with probabilities,
    red flags, and recommended diagnostic tests.
    
    The analysis considers:
    - Patient demographics and medical history
    - Symptom characteristics (severity, onset, duration)
    - Vital signs
    - Age-appropriate conditions
    - Existing comorbidities
    
    Returns structured output with diagnoses ranked by probability.
    
    Args:
        state: Injected clinical state containing patient data
        tool_call_id: Injected tool call identifier
    
    Returns:
        Command updating state with differential diagnosis
    """
    print(f"\n{'='*60}")
    print("🔬 SYMPTOM ANALYSIS - Generating Differential Diagnosis")
    print(f"{'='*60}\n")
    
    # Create analysis prompt
    prompt = create_symptom_analysis_prompt(state)
    
    # Get structured output from LLM
    structured_model = symptom_analysis_model.with_structured_output(
        SymptomAnalysisResult
    )
    
    try:
        result = structured_model.invoke(prompt)
        
        # Convert Diagnosis objects to dicts for state
        diagnoses_dict = [
            {
                "condition": d.condition,
                "probability": d.probability,
                "reasoning": d.reasoning,
                "typical_symptoms": d.typical_symptoms,
                "red_flags": d.red_flags,
                "icd10_code": d.icd10_code
            }
            for d in result.diagnoses
        ]
        
        # Print analysis results
        print("📊 DIFFERENTIAL DIAGNOSIS:")
        for i, dx in enumerate(result.diagnoses, 1):
            print(f"\n{i}. {dx.condition} ({dx.probability*100:.1f}% probability)")
            print(f"   Reasoning: {dx.reasoning[:100]}...")
            if dx.red_flags:
                print(f"   ⚠️  Red Flags: {', '.join(dx.red_flags)}")
        
        if result.red_flags:
            print(f"\n🚨 CRITICAL RED FLAGS:")
            for flag in result.red_flags:
                print(f"   • {flag}")
        
        print(f"\n🧪 RECOMMENDED TESTS: {', '.join(result.recommended_tests)}")
        print(f"📈 URGENCY: {result.urgency_level.upper()}")
        print(f"\n{'='*60}\n")
        
        # Create summary for tool message
        summary = f"""✅ Symptom Analysis Complete

Top Diagnosis: {result.diagnoses[0].condition} ({result.diagnoses[0].probability*100:.1f}%)

Differential Diagnoses ({len(result.diagnoses)}):
{chr(10).join([f'  {i+1}. {d.condition} - {d.probability*100:.1f}%' for i, d in enumerate(result.diagnoses)])}

Urgency: {result.urgency_level.upper()}
Recommended Tests: {', '.join(result.recommended_tests)}
{f'🚨 RED FLAGS: {", ".join(result.red_flags)}' if result.red_flags else ''}
"""
        
        # Combine all red flags
        all_red_flags = result.red_flags.copy()
        for dx in result.diagnoses:
            all_red_flags.extend(dx.red_flags)
        
        # Update state
        return Command(update={
            "differential_diagnosis": diagnoses_dict,
            "recommended_tests": result.recommended_tests,
            "safety_alerts": state.get("safety_alerts", []) + all_red_flags,
            "confidence_scores": {
                **state.get("confidence_scores", {}),
                "diagnosis": result.diagnoses[0].probability if result.diagnoses else 0.0
            },
            "requires_human_review": (
                state.get("requires_human_review", False) or 
                result.urgency_level == "emergent" or
                len(all_red_flags) > 0
            ),
            "messages": state.get("messages", []) + [
                ToolMessage(content=summary, tool_call_id=tool_call_id)
            ]
        })
        
    except Exception as e:
        error_msg = f"❌ Error during symptom analysis: {str(e)}"
        print(error_msg)
        
        return Command(update={
            "messages": state.get("messages", []) + [
                ToolMessage(content=error_msg, tool_call_id=tool_call_id)
            ],
            "safety_alerts": state.get("safety_alerts", []) + [
                "Symptom analysis failed - manual review required"
            ],
            "requires_human_review": True
        })


def generate_differential_diagnosis(
    symptoms: List[str],
    patient_age: int,
    patient_sex: str
) -> List[dict]:
    """
    Standalone function to generate differential diagnosis
    (for use outside of LangGraph workflow)
    
    Args:
        symptoms: List of symptom descriptions
        patient_age: Patient age in years
        patient_sex: Patient sex (M/F/Other)
    
    Returns:
        List of diagnosis dictionaries
    """
    prompt = f"""Generate differential diagnosis for:

Patient: {patient_age}yo {patient_sex}
Symptoms: {', '.join(symptoms)}

Provide 3-5 most likely diagnoses with probabilities."""

    structured_model = symptom_analysis_model.with_structured_output(
        SymptomAnalysisResult
    )
    
    result = structured_model.invoke(prompt)
    
    return [
        {
            "condition": d.condition,
            "probability": d.probability,
            "reasoning": d.reasoning
        }
        for d in result.diagnoses
    ]


# Red flag patterns for common emergency conditions
EMERGENCY_RED_FLAGS = {
    "cardiac": [
        "crushing chest pain",
        "radiating to left arm",
        "severe shortness of breath with chest pain",
        "syncope with chest pain"
    ],
    "neurologic": [
        "worst headache of life",
        "sudden severe headache",
        "neck stiffness with fever",
        "altered mental status",
        "new onset seizure",
        "focal neurological deficit"
    ],
    "respiratory": [
        "severe respiratory distress",
        "cyanosis",
        "stridor",
        "inability to speak in full sentences"
    ],
    "gastrointestinal": [
        "severe abdominal pain with rigidity",
        "hematemesis",
        "bright red blood per rectum with hypotension"
    ],
    "pediatric": [
        "inconsolable crying in infant",
        "lethargy in child",
        "difficulty breathing in child"
    ]
}


def detect_red_flags(symptoms: List[str], patient_age: int) -> List[str]:
    """
    Detect emergency red flags in symptoms
    
    Args:
        symptoms: List of symptom descriptions
        patient_age: Patient age
    
    Returns:
        List of detected red flags
    """
    detected_flags = []
    
    # Convert symptoms to lowercase for matching
    symptom_text = " ".join(symptoms).lower()
    
    # Check cardiac red flags
    for flag in EMERGENCY_RED_FLAGS["cardiac"]:
        if flag in symptom_text:
            detected_flags.append(f"CARDIAC EMERGENCY: {flag}")
    
    # Check neurologic red flags
    for flag in EMERGENCY_RED_FLAGS["neurologic"]:
        if flag in symptom_text:
            detected_flags.append(f"NEUROLOGIC EMERGENCY: {flag}")
    
    # Check respiratory red flags
    for flag in EMERGENCY_RED_FLAGS["respiratory"]:
        if flag in symptom_text:
            detected_flags.append(f"RESPIRATORY EMERGENCY: {flag}")
    
    # Check GI red flags
    for flag in EMERGENCY_RED_FLAGS["gastrointestinal"]:
        if flag in symptom_text:
            detected_flags.append(f"GI EMERGENCY: {flag}")
    
    # Check pediatric red flags if patient is pediatric
    if patient_age < 18:
        for flag in EMERGENCY_RED_FLAGS["pediatric"]:
            if flag in symptom_text:
                detected_flags.append(f"PEDIATRIC EMERGENCY: {flag}")
    
    return detected_flags
