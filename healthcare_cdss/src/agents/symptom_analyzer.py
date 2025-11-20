"""
Symptom Analyzer Agent

This module implements the symptom analysis agent node for the CDSS workflow.
It coordinates symptom analysis and medical literature search.
"""

from typing import Literal
from langgraph.types import Command

from ..state.healthcare_state import ClinicalState
from ..config.langsmith_config import trace_clinical_workflow
from ..tools.symptom_tools import analyze_symptoms_tool
from ..tools.pubmed_search import search_medical_literature


@trace_clinical_workflow("symptom_analysis")
def symptom_analyzer_node(state: ClinicalState) -> ClinicalState:
    """
    Symptom analysis node
    
    This node performs comprehensive symptom analysis:
    1. Analyzes symptoms to generate differential diagnosis
    2. Searches medical literature for supporting evidence
    3. Updates confidence scores
    4. Flags cases requiring human review
    
    Args:
        state: Current clinical state
    
    Returns:
        Updated state with analysis results
    """
    print(f"\n{'='*60}")
    print("🧠 SYMPTOM ANALYZER AGENT - Starting Analysis")
    print(f"{'='*60}\n")
    
    # Step 1: Perform symptom analysis
    print("Step 1: Analyzing symptoms...")
    
    # Analyze symptoms (this updates the state via Command)
    # In actual LangGraph execution, tools are called by the agent
    # For this node, we'll directly invoke the analysis
    
    result = analyze_symptoms_tool.invoke({
        "state": state,
        "tool_call_id": f"symptom_analysis_{state['session_id'][:8]}"
    })
    
    # Update state with analysis results
    updated_state = {**state}
    if hasattr(result, 'update') and result.update:
        for key, value in result.update.items():
            updated_state[key] = value
    
    # Step 2: Search medical literature and web if needed
    if updated_state.get("differential_diagnosis"):
        top_diagnosis = updated_state["differential_diagnosis"][0]["condition"]
        
        print(f"\nStep 2: Searching medical sources for: {top_diagnosis}")
        
        # Search PubMed for peer-reviewed literature
        lit_search_result = search_medical_literature.invoke({
            "clinical_question": f"{top_diagnosis} diagnosis and management",
            "state": updated_state,
            "tool_call_id": f"lit_search_{state['session_id'][:8]}",
            "max_results": 2
        })
        
        # Update state with literature findings
        if hasattr(lit_search_result, 'update') and lit_search_result.update:
            for key, value in lit_search_result.update.items():
                if key == "messages":
                    updated_state["messages"] = updated_state.get("messages", []) + value
                elif key == "files":
                    updated_state["files"] = {**updated_state.get("files", {}), **value}
                elif key == "evidence_sources":
                    updated_state["evidence_sources"] = updated_state.get("evidence_sources", []) + value
                else:
                    updated_state[key] = value
        
        # Search web for current guidelines and information (Phase 7)
        from ..tools.tavily_search import search_medical_web
        
        print(f"\nStep 2b: Searching web for current information...")
        
        web_search_result = search_medical_web.invoke({
            "clinical_question": f"{top_diagnosis} clinical guidelines and current information",
            "state": updated_state,
            "tool_call_id": f"web_search_{state['session_id'][:8]}",
            "max_results": 2
        })
        
        # Update state with web search findings
        if hasattr(web_search_result, 'update') and web_search_result.update:
            for key, value in web_search_result.update.items():
                if key == "messages":
                    updated_state["messages"] = updated_state.get("messages", []) + value
                elif key == "files":
                    updated_state["files"] = {**updated_state.get("files", {}), **value}
                elif key == "evidence_sources":
                    updated_state["evidence_sources"] = updated_state.get("evidence_sources", []) + value
                else:
                    updated_state[key] = value
    
    # Step 3: Update TODO status
    todos = updated_state.get("todos", [])
    for todo in todos:
        if "symptom analysis" in todo["content"].lower():
            todo["status"] = "completed"
            todo["assigned_agent"] = "symptom_analyzer"
    
    updated_state["todos"] = todos
    
    print(f"\n{'='*60}")
    print("✅ SYMPTOM ANALYZER - Analysis Complete")
    print(f"{'='*60}\n")
    
    return updated_state


def should_search_literature(state: ClinicalState) -> bool:
    """
    Determine if literature search is needed
    
    Args:
        state: Current clinical state
    
    Returns:
        True if literature search should be performed
    """
    # Search literature if:
    # 1. Diagnosis confidence is low
    # 2. Case is complex (multiple chronic conditions)
    # 3. Rare condition suspected
    
    if not state.get("differential_diagnosis"):
        return False
    
    top_diagnosis = state["differential_diagnosis"][0]
    confidence = top_diagnosis.get("probability", 0.0)
    
    # Low confidence
    if confidence < 0.7:
        return True
    
    # Multiple chronic conditions
    if len(state["patient_info"].chronic_conditions) >= 3:
        return True
    
    # Rare condition keywords
    rare_keywords = ["rare", "uncommon", "atypical", "unusual"]
    diagnosis_text = top_diagnosis.get("condition", "").lower()
    
    if any(keyword in diagnosis_text for keyword in rare_keywords):
        return True
    
    return False


@trace_clinical_workflow("literature_research")
def literature_research_node(state: ClinicalState) -> ClinicalState:
    """
    Dedicated literature research node
    
    This node performs in-depth medical literature research
    when needed (low confidence, complex cases, rare conditions)
    
    Args:
        state: Current clinical state
    
    Returns:
        Updated state with literature findings
    """
    if not should_search_literature(state):
        print("📚 Literature search not needed (high confidence diagnosis)")
        return state
    
    print(f"\n{'='*60}")
    print("📚 LITERATURE RESEARCH - Deep Dive")
    print(f"{'='*60}\n")
    
    updated_state = {**state}
    
    # Search for each diagnosis in top 3
    for i, diagnosis in enumerate(state.get("differential_diagnosis", [])[:3], 1):
        condition = diagnosis["condition"]
        
        print(f"\nResearching {i}: {condition}")
        
        result = search_medical_literature.invoke({
            "clinical_question": f"{condition} clinical presentation and diagnosis",
            "state": updated_state,
            "tool_call_id": f"deep_research_{i}_{state['session_id'][:8]}",
            "max_results": 2
        })
        
        # Update state
        if hasattr(result, 'update') and result.update:
            for key, value in result.update.items():
                if key == "messages":
                    updated_state["messages"] = updated_state.get("messages", []) + value
                elif key == "files":
                    updated_state["files"] = {**updated_state.get("files", {}), **value}
                elif key == "evidence_sources":
                    updated_state["evidence_sources"] = updated_state.get("evidence_sources", []) + value
                else:
                    updated_state[key] = value
    
    print(f"\n{'='*60}")
    print("✅ LITERATURE RESEARCH - Complete")
    print(f"{'='*60}\n")
    
    return updated_state
