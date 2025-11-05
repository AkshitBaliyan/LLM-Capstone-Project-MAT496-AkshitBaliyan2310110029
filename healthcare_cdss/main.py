"""
Main entry point for Healthcare CDSS

Run this script to:
1. Set up LangSmith
2. Test the Phase 1 workflow
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.state import PatientInfo, Symptom, create_initial_state
from src.agents import create_clinical_workflow, run_clinical_analysis
from src.config import setup_phase1_langsmith


def main():
    """Main entry point"""
    
    print("\n" + "="*60)
    print("🏥 HEALTHCARE CLINICAL DECISION SUPPORT SYSTEM")
    print("   Phase 1: Foundation & Setup")
    print("="*60 + "\n")
    
    # Step 1: Set up LangSmith (optional, will warn if no API key)
    print("Step 1: Setting up LangSmith...")
    try:
        setup_phase1_langsmith()
    except Exception as e:
        print(f"⚠️  LangSmith setup skipped: {e}")
        print("   (You can still run the workflow without LangSmith)\n")
    
    # Step 2: Create sample patient case
    print("\nStep 2: Creating sample clinical case...")
    
    patient = PatientInfo(
        patient_id="P12345",
        age=45,
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
    
    initial_state = create_initial_state(
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
    
    print(f"✅ Created case for {patient.age}yo {patient.sex} patient")
    print(f"   Chief Complaint: {initial_state['chief_complaint']}")
    print(f"   Symptoms: {len(symptoms)}")
    
    # Step 3: Run clinical analysis
    print("\nStep 3: Running clinical analysis workflow...")
    
    result = run_clinical_analysis(initial_state)
    
    # Step 4: Display results
    print("\n" + "="*60)
    print("📊 ANALYSIS RESULTS")
    print("="*60)
    
    print("\n📋 Analysis Tasks Generated:")
    for i, todo in enumerate(result['todos'], 1):
        status_icon = "✓" if todo['status'] == "completed" else "○"
        print(f"   {status_icon} [{todo['priority'].upper()}] {todo['content']}")
    
    if result['safety_alerts']:
        print("\n🚨 Safety Alerts:")
        for alert in result['safety_alerts']:
            print(f"   • {alert}")
    
    if result['requires_human_review']:
        print("\n⚕️  Human Review Required:")
        for reason in result['review_reasons']:
            print(f"   • {reason}")
    
    print("\n💬 Agent Messages:")
    for msg in result['messages'][-2:]:  # Show last 2 messages
        msg_type = "User" if hasattr(msg, 'type') and msg.type == "human" else "AI"
        content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        print(f"   [{msg_type}] {content_preview}")
    
    print("\n" + "="*60)
    print("✅ Phase 1 Demo Complete!")
    print("="*60)
    print("\nNext Steps:")
    print("  1. Review the generated analysis tasks")
    print("  2. Check LangSmith for execution traces")
    print("  3. Move to Phase 2 to implement symptom analysis agent")
    print()


if __name__ == "__main__":
    main()
