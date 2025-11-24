"""
Healthcare CDSS - Main Orchestrator

This module implements the main workflow orchestrator for the Clinical
Decision Support System. In Phase 1, it provides a basic workflow skeleton
that will be expanded in later phases.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage

from ..state.healthcare_state import ClinicalState, add_todo, add_safety_alert
from ..config.langsmith_config import trace_clinical_workflow


# Initialize LLM
model = init_chat_model(
    "openai:gpt-4o",
    temperature=0.0  # Deterministic for clinical decisions
)


@trace_clinical_workflow("analyze_case")
def analyze_case_node(state: ClinicalState) -> ClinicalState:
    """
    Initial case analysis node
    
    This node:
    1. Receives patient information and symptoms
    2. Performs initial assessment
    3. Identifies if case is critical/urgent
    4. Provides preliminary analysis
    
    Args:
        state: Current clinical state
    
    Returns:
        Updated state with initial analysis
    """
    # Extract key information
    patient = state["patient_info"]
    complaint = state["chief_complaint"]
    symptoms = state["symptoms"]
    vitals = state["vital_signs"]
    
    # Build context for LLM
    symptoms_text = "\n".join([
        f"- {s.description}: {s.severity} severity, onset {s.onset}"
        for s in symptoms
    ])
    
    vitals_text = "\n".join([
        f"- {k}: {v}"
        for k, v in vitals.items()
    ])
    
    # Create analysis prompt
    analysis_prompt = f"""You are a clinical decision support system performing initial case triage.

PATIENT INFORMATION:
- Age: {patient.age} years
- Sex: {patient.sex}
- BMI: {patient.get_bmi()}
- Allergies: {', '.join(patient.allergies) if patient.allergies else 'None reported'}
- Current Medications: {', '.join(patient.current_medications) if patient.current_medications else 'None'}
- Chronic Conditions: {', '.join(patient.chronic_conditions) if patient.chronic_conditions else 'None'}

CHIEF COMPLAINT:
{complaint}

SYMPTOMS:
{symptoms_text}

VITAL SIGNS:
{vitals_text}

TASK:
Provide a brief initial assessment including:
1. Acuity level (routine, urgent, emergent)
2. Key clinical observations
3. Any immediate red flags
4. Preliminary differential diagnosis considerations

Format your response as a structured analysis."""

    # Get LLM response
    response = model.invoke([HumanMessage(content=analysis_prompt)])
    
    # Add response to messages
    updated_state = {
        **state,
        "messages": state["messages"] + [
            HumanMessage(content=f"Analyzing case: {complaint}"),
            response
        ]
    }
    
    # Check for critical keywords in response
    response_text = response.content.lower()
    critical_keywords = ["emergent", "emergency", "critical", "stat", "immediate"]
    
    if any(keyword in response_text for keyword in critical_keywords):
        updated_state = add_safety_alert(
            updated_state,
            "Case flagged as potentially critical - urgent evaluation required",
            require_review=True
        )
    
    # Log analysis
    print(f"\n{'='*60}")
    print(f"CASE ANALYSIS - Session: {state['session_id'][:8]}")
    print(f"{'='*60}")
    print(f"Patient: {patient.age}yo {patient.sex}")
    print(f"Complaint: {complaint}")
    print(f"Initial Assessment Generated")
    print(f"{'='*60}\n")
    
    return updated_state


@trace_clinical_workflow("generate_todos")
def generate_todos_node(state: ClinicalState) -> ClinicalState:
    """
    Generate TODO list for clinical analysis
    
    This node decides what analyses need to be performed based on
    the initial case assessment.
    
    Args:
        state: Current clinical state
    
    Returns:
        Updated state with TODO list
    """
    # Basic TODO generation (will be expanded in Phase 2+)
    updated_state = state.copy()
    
    # Always add symptom analysis
    updated_state = add_todo(
        updated_state,
        "Perform detailed symptom analysis and generate differential diagnosis",
        priority="high"
    )
    
    # Add medication review if patient is on medications
    if state["patient_info"].current_medications:
        updated_state = add_todo(
            updated_state,
            "Review current medications for interactions and contraindications",
            priority="high"
        )
    
    # Add literature search TODO
    updated_state = add_todo(
        updated_state,
        f"Search medical literature for: {state['chief_complaint']}",
        priority="medium"
    )
    
    print(f"📋 Generated {len(updated_state['todos'])} analysis tasks")
    for i, todo in enumerate(updated_state['todos'], 1):
        print(f"   {i}. [{todo['priority'].upper()}] {todo['content']}")
    
    return updated_state


@trace_clinical_workflow("safety_check")
def safety_check_node(state: ClinicalState) -> ClinicalState:
    """
    Perform initial safety checks
    
    This node performs basic safety validation:
    - Check for pediatric/geriatric special considerations
    - Verify allergies are documented
    - Flag high-risk patient factors
    
    Args:
        state: Current clinical state
    
    Returns:
        Updated state with safety checks performed
    """
    updated_state = state.copy()
    patient = state["patient_info"]
    
    # Pediatric check
    if patient.is_pediatric():
        updated_state = add_safety_alert(
            updated_state,
            f"PEDIATRIC PATIENT (Age: {patient.age}) - Age-appropriate dosing required",
            require_review=True
        )
    
    # Geriatric check
    if patient.is_geriatric():
        updated_state = add_safety_alert(
            updated_state,
            f"GERIATRIC PATIENT (Age: {patient.age}) - Consider reduced dosing and drug interactions",
            require_review=False  # Warning but not blocking
        )
    
    # Check for multiple chronic conditions (polypharmacy risk)
    if len(patient.chronic_conditions) >= 3:
        updated_state = add_safety_alert(
            updated_state,
            f"MULTIPLE CHRONIC CONDITIONS ({len(patient.chronic_conditions)}) - Enhanced monitoring required",
            require_review=False
        )
    
    # Check if allergy information is documented
    if not patient.allergies:
        print("⚠️  No allergies documented - should verify with patient")
    
    # Print safety summary
    if updated_state["safety_alerts"]:
        print(f"\n🚨 SAFETY ALERTS ({len(updated_state['safety_alerts'])}):")
        for alert in updated_state["safety_alerts"]:
            print(f"   - {alert}")
        print()
    
    # Set review reasons
    if updated_state["requires_human_review"] and not updated_state["review_reasons"]:
        updated_state["review_reasons"] = ["Safety alerts require human review"]
    
    return updated_state


def create_clinical_workflow() -> StateGraph:
    """
    Create the main CDSS workflow graph
    
    Phase 2 workflow includes symptom analysis:
    analyze_case -> generate_todos -> symptom_analyzer -> safety_check -> END
    
    The symptom_analyzer node performs:
    - Differential diagnosis generation
    - Medical literature search
    - Evidence collection
    
    Returns:
        Compiled LangGraph workflow
    """
    from .symptom_analyzer import symptom_analyzer_node
    
    # Create workflow graph
    workflow = StateGraph(ClinicalState)
    
    # Add nodes
    workflow.add_node("analyze_case", analyze_case_node)
    workflow.add_node("generate_todos", generate_todos_node)
    workflow.add_node("symptom_analyzer", symptom_analyzer_node)  # NEW in Phase 2
    workflow.add_node("safety_check", safety_check_node)
    
    # Define flow
    workflow.set_entry_point("analyze_case")
    workflow.add_edge("analyze_case", "generate_todos")
    workflow.add_edge("generate_todos", "symptom_analyzer")  # NEW in Phase 2
    workflow.add_edge("symptom_analyzer", "safety_check")
    workflow.add_edge("safety_check", END)
    
    # Compile and return
    return workflow.compile()


def run_clinical_analysis(state: ClinicalState) -> ClinicalState:
    """
    Main entry point for running clinical analysis
    
    Args:
        state: Initial clinical state
    
    Returns:
        Final state after workflow execution
    """
    print("\n" + "="*60)
    print("🏥 HEALTHCARE CLINICAL DECISION SUPPORT SYSTEM")
    print("   Phase 1: Foundation & Basic Workflow")
    print("="*60)
    
    # Create workflow
    workflow = create_clinical_workflow()
    
    # Execute workflow
    try:
        result = workflow.invoke(state)
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE")
        print("="*60)
        
        # Print summary
        print(f"\nSession ID: {result['session_id']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Version: {result['version']}")
        
        if result["requires_human_review"]:
            print(f"\n🔍 HUMAN REVIEW REQUIRED")
            print(f"Reasons:")
            for reason in result["review_reasons"]:
                print(f"   - {reason}")
        
        print(f"\nTODOs Generated: {len(result['todos'])}")
        print(f"Safety Alerts: {len(result['safety_alerts'])}")
        print(f"Messages Exchanged: {len(result['messages'])}")
        
        print("\n" + "="*60 + "\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise


# Convenience function for quick testing
def quick_test():
    """
    Quick test of the workflow with a sample case
    """
    from ..state.healthcare_state import create_initial_state, PatientInfo, Symptom
    
    # Create sample patient
    patient = PatientInfo(
        patient_id="P001",
        age=45,
        sex="M",
        weight_kg=80.0,
        height_cm=175.0,
        allergies=["Penicillin"],
        current_medications=["Lisinopril 10mg daily"],
        chronic_conditions=["Hypertension"]
    )
    
    # Create symptoms
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
        )
    ]
    
    # Create initial state
    state = create_initial_state(
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
    
    # Run analysis
    result = run_clinical_analysis(state)
    
    return result


if __name__ == "__main__":
    print("Running quick test of Phase 1 workflow...\n")
    quick_test()
