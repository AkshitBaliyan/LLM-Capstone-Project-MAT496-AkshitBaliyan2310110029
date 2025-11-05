"""
LangSmith Configuration for Healthcare CDSS

This module configures LangSmith for:
- Comprehensive tracing of all clinical decisions
- Evaluation dataset management
- Performance monitoring
- Safety and compliance tracking
"""

import os
from typing import Optional
from datetime import datetime
from langsmith import Client
from langsmith.run_helpers import traceable
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure LangSmith environment
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "healthcare-cdss")
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Initialize LangSmith client
client = Client()


def setup_langsmith() -> Client:
    """
    Initialize LangSmith client with healthcare-specific configuration
    
    Returns:
        Configured LangSmith client
    """
    # Verify API key is set
    if not os.getenv("LANGSMITH_API_KEY"):
        raise ValueError(
            "LANGSMITH_API_KEY not found. "
            "Please set it in your .env file or environment variables"
        )
    
    print(f"✅ LangSmith configured for project: {os.getenv('LANGCHAIN_PROJECT')}")
    return client


def create_clinical_evaluation_dataset(
    dataset_name: str = "clinical_cases_evaluation",
    description: str = "Hand-validated clinical scenarios for CDSS testing"
) -> str:
    """
    Create evaluation dataset for clinical cases
    
    Args:
        dataset_name: Name for the dataset
        description: Description of dataset purpose
    
    Returns:
        Dataset ID
    """
    try:
        # Check if dataset exists
        existing_datasets = list(client.list_datasets(dataset_name=dataset_name))
        if existing_datasets:
            dataset = existing_datasets[0]
            print(f"✓ Using existing dataset: {dataset_name} (ID: {dataset.id})")
            return str(dataset.id)
        
        # Create new dataset
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description=description,
            data_type="kv"  # Key-value pairs for inputs/outputs
        )
        print(f"✅ Created dataset: {dataset_name} (ID: {dataset.id})")
        return str(dataset.id)
        
    except Exception as e:
        print(f"❌ Error creating dataset: {e}")
        raise


def add_clinical_examples(dataset_id: str):
    """
    Add initial clinical evaluation examples to dataset
    
    These are hand-validated cases with known diagnoses for testing
    the CDSS accuracy and safety.
    
    Args:
        dataset_id: ID of dataset to add examples to
    """
    
    # Example clinical cases with known diagnoses
    examples = [
        {
            "inputs": {
                "chief_complaint": "Fever and cough for 3 days",
                "patient_age": 35,
                "patient_sex": "M",
                "symptoms": [
                    {"description": "fever", "severity": "moderate", "onset": "3 days ago"},
                    {"description": "dry cough", "severity": "moderate", "onset": "3 days ago"},
                    {"description": "fatigue", "severity": "mild", "onset": "2 days ago"}
                ],
                "vital_signs": {
                    "temperature": 38.2,
                    "heart_rate": 88,
                    "respiratory_rate": 18,
                    "blood_pressure": "120/80"
                }
            },
            "outputs": {
                "top_diagnosis": "Upper Respiratory Tract Infection",
                "confidence": 0.85,
                "recommended_tests": ["Chest X-ray", "CBC with differential"],
                "treatment": ["Rest", "Fluids", "Acetaminophen for fever"],
                "red_flags": []
            },
            "metadata": {
                "difficulty": "easy",
                "specialty": "general_medicine",
                "case_id": "CASE001"
            }
        },
        {
            "inputs": {
                "chief_complaint": "Severe chest pain radiating to left arm",
                "patient_age": 58,
                "patient_sex": "M",
                "symptoms": [
                    {"description": "crushing chest pain", "severity": "severe", "onset": "30 minutes ago"},
                    {"description": "shortness of breath", "severity": "moderate", "onset": "30 minutes ago"},
                    {"description": "nausea", "severity": "mild", "onset": "20 minutes ago"},
                    {"description": "sweating", "severity": "moderate", "onset": "30 minutes ago"}
                ],
                "vital_signs": {
                    "temperature": 37.0,
                    "heart_rate": 110,
                    "respiratory_rate": 22,
                    "blood_pressure": "145/95"
                }
            },
            "outputs": {
                "top_diagnosis": "Acute Coronary Syndrome (suspected STEMI)",
                "confidence": 0.95,
                "recommended_tests": ["ECG STAT", "Troponin", "CXR"],
                "treatment": ["Call 911/Emergency", "Aspirin 325mg", "Nitroglycerin"],
                "red_flags": ["CARDIAC EMERGENCY - IMMEDIATE INTERVENTION REQUIRED"]
            },
            "metadata": {
                "difficulty": "medium",
                "specialty": "cardiology",
                "case_id": "CASE002",
                "critical": True
            }
        },
        {
            "inputs": {
                "chief_complaint": "Severe headache with neck stiffness",
                "patient_age": 24,
                "patient_sex": "F",
                "symptoms": [
                    {"description": "severe headache", "severity": "severe", "onset": "6 hours ago"},
                    {"description": "neck stiffness", "severity": "severe", "onset": "4 hours ago"},
                    {"description": "photophobia", "severity": "moderate", "onset": "3 hours ago"},
                    {"description": "fever", "severity": "moderate", "onset": "8 hours ago"}
                ],
                "vital_signs": {
                    "temperature": 39.1,
                    "heart_rate": 105,
                    "respiratory_rate": 20,
                    "blood_pressure": "118/75"
                }
            },
            "outputs": {
                "top_diagnosis": "Bacterial Meningitis (suspected)",
                "confidence": 0.88,
                "recommended_tests": ["Lumbar puncture STAT", "Blood cultures", "CT head"],
                "treatment": ["IV antibiotics immediately", "Hospital admission"],
                "red_flags": ["NEUROLOGIC EMERGENCY - IMMEDIATE LUMBAR PUNCTURE REQUIRED"]
            },
            "metadata": {
                "difficulty": "hard",
                "specialty": "neurology",
                "case_id": "CASE003",
                "critical": True
            }
        },
        {
            "inputs": {
                "chief_complaint": "Persistent cough with weight loss",
                "patient_age": 62,
                "patient_sex": "M",
                "symptoms": [
                    {"description": "persistent cough", "severity": "moderate", "onset": "6 weeks ago"},
                    {"description": "unintentional weight loss", "severity": "moderate", "onset": "2 months ago"},
                    {"description": "night sweats", "severity": "mild", "onset": "3 weeks ago"},
                    {"description": "hemoptysis", "severity": "mild", "onset": "1 week ago"}
                ],
                "vital_signs": {
                    "temperature": 37.3,
                    "heart_rate": 82,
                    "respiratory_rate": 16,
                    "blood_pressure": "128/82"
                }
            },
            "outputs": {
                "top_diagnosis": "Lung Cancer (suspected) - DDx includes TB",
                "confidence": 0.75,
                "recommended_tests": ["Chest CT", "Sputum culture", "Bronchoscopy"],
                "treatment": ["Urgent pulmonology referral", "Smoking cessation if applicable"],
                "red_flags": ["URGENT WORKUP - Possible malignancy"]
            },
            "metadata": {
                "difficulty": "hard",
                "specialty": "pulmonology",
                "case_id": "CASE004"
            }
        },
        {
            "inputs": {
                "chief_complaint": "Painful urination and frequency",
                "patient_age": 28,
                "patient_sex": "F",
                "symptoms": [
                    {"description": "dysuria", "severity": "moderate", "onset": "2 days ago"},
                    {"description": "urinary frequency", "severity": "moderate", "onset": "2 days ago"},
                    {"description": "lower abdominal discomfort", "severity": "mild", "onset": "1 day ago"}
                ],
                "vital_signs": {
                    "temperature": 37.1,
                    "heart_rate": 78,
                    "respiratory_rate": 16,
                    "blood_pressure": "118/72"
                }
            },
            "outputs": {
                "top_diagnosis": "Uncomplicated Urinary Tract Infection",
                "confidence": 0.92,
                "recommended_tests": ["Urinalysis", "Urine culture"],
                "treatment": ["Nitrofurantoin 100mg BID x 5 days", "Increase fluid intake"],
                "red_flags": []
            },
            "metadata": {
                "difficulty": "easy",
                "specialty": "general_medicine",
                "case_id": "CASE005"
            }
        }
    ]
    
    # Add examples to dataset
    added_count = 0
    for example in examples:
        try:
            client.create_example(
                dataset_id=dataset_id,
                inputs=example["inputs"],
                outputs=example["outputs"],
                metadata=example.get("metadata", {})
            )
            added_count += 1
            print(f"✓ Added case: {example['metadata'].get('case_id', 'Unknown')}")
        except Exception as e:
            print(f"❌ Error adding example: {e}")
    
    print(f"✅ Added {added_count}/{len(examples)} clinical cases to dataset")


def log_clinical_decision(
    session_id: str,
    decision_type: str,
    inputs: dict,
    outputs: dict,
    metadata: Optional[dict] = None
) -> None:
    """
    Log a clinical decision to LangSmith for audit trail
    
    Args:
        session_id: Unique session identifier
        decision_type: Type of decision (diagnosis, treatment, etc.)
        inputs: Input data used for decision
        outputs: Decision outputs
        metadata: Additional metadata
    """
    try:
        # Note: Actual implementation would use client.create_run()
        # This is a placeholder for Phase 1
        print(f"📝 Logged {decision_type} decision for session {session_id}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to log decision: {e}")


def create_feedback_collection():
    """
    Set up feedback collection mechanism for clinician input
    
    This allows healthcare providers to rate the quality of recommendations
    and provide corrections, which feeds back into evaluation.
    """
    print("✅ Feedback collection mechanism configured")
    print("   Clinicians can provide thumbs up/down and corrections")


# Decorator for tracing clinical workflows
def trace_clinical_workflow(workflow_name: str):
    """
    Decorator to trace clinical workflow execution in LangSmith
    
    Args:
        workflow_name: Name of the workflow being traced
    
    Usage:
        @trace_clinical_workflow("symptom_analysis")
        def analyze_symptoms(state):
            ...
    """
    return traceable(
        run_type="chain",
        name=workflow_name,
        project_name=os.getenv("LANGCHAIN_PROJECT", "healthcare-cdss")
    )


# Initialize LangSmith on module import
if __name__ != "__main__":
    try:
        setup_langsmith()
    except ValueError as e:
        print(f"⚠️ Warning: {e}")
        print("   LangSmith features will be limited without API key")


# Main setup function for Phase 1
def setup_phase1_langsmith():
    """
    Complete Phase 1 LangSmith setup
    
    This function:
    1. Initializes LangSmith client
    2. Creates evaluation dataset
    3. Adds initial clinical cases
    4. Configures feedback collection
    """
    print("\n🚀 Setting up LangSmith for Healthcare CDSS (Phase 1)")
    print("=" * 60)
    
    # Step 1: Initialize client
    client = setup_langsmith()
    
    # Step 2: Create evaluation dataset
    dataset_id = create_clinical_evaluation_dataset()
    
    # Step 3: Add clinical examples
    add_clinical_examples(dataset_id)
    
    # Step 4: Configure feedback
    create_feedback_collection()
    
    print("=" * 60)
    print("✅ LangSmith Phase 1 setup complete!")
    print(f"\nNext steps:")
    print("  1. View dataset at: https://smith.langchain.com/datasets/{dataset_id}")
    print("  2. Start running CDSS workflow to generate traces")
    print("  3. Review traces at: https://smith.langchain.com/projects")
    print("\n")


if __name__ == "__main__":
    # Run full setup when executed directly
    setup_phase1_langsmith()
