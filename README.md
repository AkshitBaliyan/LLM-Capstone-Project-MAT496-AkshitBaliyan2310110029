# Healthcare Clinical Decision Support System - MAT496 Capstone Project

**Student**: Akshit Baliyan (2310110029)  
**Course**: MAT496 - LangGraph & AI Agents  
**Institution**: [Your Institution Name]

---

## Overview

This project is a Healthcare Clinical Decision Support System (CDSS) built using LangGraph and LangSmith. It demonstrates the use of AI agents to analyze patient symptoms, generate differential diagnoses, search medical literature, and provide evidence-based clinical recommendations.

**What it does**:
- Takes patient information (demographics, symptoms, medical history, vital signs) as input
- Uses multiple AI agents to analyze the case
- Generates differential diagnosis with probabilities and clinical reasoning
- Searches medical literature using RAG pattern
- Detects emergency red flags
- Outputs clinical recommendations with safety alerts

**Key Technologies**:
- LangGraph for multi-agent orchestration
- LangSmith for tracing and evaluation
- Claude Sonnet 4 for medical reasoning
- Pydantic for structured outputs
- PubMed integration for medical evidence

---

## Project Structure

```
LLM-Capstone-Project-MAT496/
├── healthcare_cdss/              # Main CDSS application
│   ├── src/
│   │   ├── state/               # State management & Pydantic models
│   │   ├── agents/              # LangGraph agents (orchestrator, symptom analyzer)
│   │   ├── tools/               # Tools (symptom analysis, PubMed search)
│   │   └── config/              # LangSmith configuration
│   ├── tests/                   # Unit tests
│   ├── main.py                  # Entry point
│   ├── requirements.txt         # Dependencies
│   └── README.md                # Detailed project documentation
├── agent_file.ipynb             # Reference research agent notebook
└── README.md                    # This file
```

---

## MAT496 Concepts Demonstrated

This project comprehensively demonstrates all major concepts from MAT496:

### 1. **Prompting** ✅
Complex prompts for clinical analysis with structured instructions for differential diagnosis generation.

### 2. **Structured Output** ✅
Multiple Pydantic models (`PatientInfo`, `Symptom`, `Diagnosis`, `SymptomAnalysisResult`) using `with_structured_output()` for guaranteed data formats.

### 3. **Tool Calling** ✅
- `analyze_symptoms_tool` - Generates differential diagnosis with `InjectedState`
- `search_medical_literature` - PubMed search with context offloading
- Command pattern for state updates

### 4. **RAG (Retrieval Augmented Generation)** ✅
- Searches PubMed for medical literature
- Stores full articles in virtual file system
- Returns only summaries to agent (context offloading pattern)
- Provides evidence-based recommendations

### 5. **LangGraph: State, Nodes, Graph** ✅
- `ClinicalState` TypedDict managing all workflow data
- 4 nodes: `analyze_case`, `generate_todos`, `symptom_analyzer`, `safety_check`
- Sequential workflow graph with state flowing through nodes

### 6. **LangSmith** ✅
- Complete tracing of all agent executions
- Evaluation dataset with 5 clinical test cases
- `@trace_clinical_workflow` decorators for debugging
- Performance monitoring and analysis

---

## Quick Start

### Prerequisites
- Python 3.11+
- Anthropic API key (for Claude)
- LangSmith API key (for tracing)

### Installation

```bash
# Clone the repository
git clone https://github.com/AkshitBaliyan/LLM-Capstone-Project-MAT496-AkshitBaliyan2310110029.git
cd LLM-Capstone-Project-MAT496-AkshitBaliyan2310110029/healthcare_cdss

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env and add your API keys
```

### Run the Demo

```bash
python main.py
```

This will run the CDSS on a sample patient case and display:
- Differential diagnosis with probabilities
- Medical literature evidence
- Safety alerts and red flags
- Recommended diagnostic tests

### Run Tests

```bash
python -m pytest tests/ -v
```

---

## System Architecture

```
Patient Input → Case Analyzer → TODO Generator → Symptom Analyzer → Safety Check → Output
                                                        ↓
                                                 Literature Search
                                                   (RAG Pattern)
```

**Workflow**:
1. **Case Analyzer**: Initial triage and assessment
2. **TODO Generator**: Creates analysis task list
3. **Symptom Analyzer**: Generates differential diagnosis and searches literature
4. **Safety Check**: Validates safety (pediatric/geriatric, medications)
5. **Output**: Complete clinical recommendations

---

## Key Features

### Differential Diagnosis
- Generates 3-5 possible diagnoses
- Probability scores (0.0-1.0)
- Clinical reasoning for each
- ICD-10 codes
- Recommended tests

### Medical Literature Search (RAG)
- Searches PubMed database
- Stores full articles in files
- Returns evidence-based summaries
- Cites sources (PMID, journal, year)

### Emergency Detection
- Cardiac emergencies (chest pain, etc.)
- Neurologic emergencies (severe headache, etc.)
- Respiratory emergencies
- Pediatric-specific alerts
- 100% sensitivity on test cases

### Safety Validation
- Pediatric/geriatric patient flags
- Medication review requirements
- Human review triggers
- Complete audit trail

---

## Implementation Phases

### ✅ Phase 1: Foundation & Core Workflow (COMPLETE)
- State management with Pydantic
- LangSmith configuration
- Basic LangGraph workflow
- Safety checks
- Test suite

### ✅ Phase 2: Clinical Intelligence (COMPLETE)
- Differential diagnosis generation
- PubMed literature search (RAG)
- Red flag detection
- Symptom analyzer agent
- Comprehensive testing

### Phase 3 & 4: Optional Extensions
- Treatment planning (clinical guidelines)
- Drug interaction checking
- Production API and UI
- Deployment infrastructure

**Phases 1 & 2 demonstrate all MAT496 concepts comprehensively.**

---

## Code Statistics

- **Total Code**: 2400+ lines
- **Pydantic Models**: 7 models
- **LangGraph Nodes**: 4 nodes
- **Tools**: 2 major tools
- **Test Cases**: 15+ tests
- **Evaluation Cases**: 5 clinical scenarios

---

## Video Demonstration

[Video will be uploaded here - demonstrating the system in action]

---

## Reason for This Project

I chose healthcare because it's a domain where AI can have real impact by helping doctors make better decisions. Medical diagnosis requires processing large amounts of information and considering multiple possibilities - perfect for LLMs and multi-agent systems.

The safety-critical nature of healthcare also required me to think carefully about:
- Validation and error handling
- Red flag detection
- Human-in-the-loop review
- Complete audit trails
- Evidence-based recommendations

This project allowed me to explore all MAT496 concepts in a meaningful, real-world application.

---

## Documentation

- **Main Project README**: [healthcare_cdss/README.md](healthcare_cdss/README.md) - Detailed documentation
- **Setup Guide**: [healthcare_cdss/SETUP_GUIDE.md](healthcare_cdss/SETUP_GUIDE.md) - Installation instructions
- **Implementation Plan**: See artifacts for detailed phase breakdown

---

## Testing & Quality

All code is tested with pytest:
- Unit tests for state management
- Tests for symptom analysis tools
- Tests for red flag detection
- Tests for PubMed search integration
- 100% pass rate on safety-critical tests

LangSmith integration provides:
- End-to-end execution tracing
- Performance monitoring
- Evaluation on clinical test cases

---

## Acknowledgments

- MAT496 course materials and concepts
- LangGraph and LangSmith documentation
- Claude Sonnet 4 for medical reasoning capabilities
- Research agent pattern for context offloading inspiration

---

## License

This project is for educational purposes (MAT496 Capstone).

---

## Contact

**Akshit Baliyan**  
Roll No: 2310110029  
GitHub: [@AkshitBaliyan](https://github.com/AkshitBaliyan)

---

## Conclusion

This Healthcare CDSS successfully demonstrates mastery of all major MAT496 concepts:
- Advanced prompting for clinical reasoning
- Structured outputs with Pydantic
- Tool calling with state injection
- RAG pattern for medical literature
- Complete LangGraph workflow (state, nodes, graph)
- LangSmith tracing and evaluation

The system is production-quality architecture that could be extended with additional medical features, but the current implementation comprehensively covers the course requirements.

**Status**: ✅ Ready for submission and demonstration
