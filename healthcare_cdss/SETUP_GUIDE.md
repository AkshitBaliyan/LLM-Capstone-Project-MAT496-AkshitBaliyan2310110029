# Healthcare CDSS - Phase 1 Setup Guide

## Quick Start Guide

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd C:\Users\hp\Desktop\Capstone_Project\healthcare_cdss

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Keys

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_actual_key_here
   LANGSMITH_API_KEY=your_actual_key_here
   ```

3. Get API keys from:
   - Anthropic: https://console.anthropic.com/
   - LangSmith: https://smith.langchain.com/

### Step 3: Run Tests

```bash
# Run the test suite
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src --cov-report=html
```

### Step 4: Run Phase 1 Demo

```bash
# Run the main demo
python main.py
```

This will:
1. Set up LangSmith with evaluation dataset
2. Create a sample clinical case
3. Run the workflow
4. Display analysis results

### Step 5: Set Up LangSmith (One-time)

```bash
# Run LangSmith setup separately if needed
python -c "from src.config import setup_phase1_langsmith; setup_phase1_langsmith()"
```

## Project Structure Created

```
healthcare_cdss/
├── src/
│   ├── __init__.py
│   ├── state/
│   │   ├── __init__.py
│   │   └── healthcare_state.py       ✅ State management
│   ├── agents/
│   │   ├── __init__.py
│   │   └── orchestrator.py           ✅ Main workflow
│   └── config/
│       ├── __init__.py
│       └── langsmith_config.py       ✅ LangSmith setup
├── tests/
│   ├── __init__.py
│   └── test_state.py                 ✅ Unit tests
├── main.py                           ✅ Entry point
├── requirements.txt                  ✅ Dependencies
├── .env.example                      ✅ Config template
├── .gitignore                        ✅ Git ignore
└── README.md                         ✅ Documentation
```

## What's Implemented (Phase 1)

### ✅ State Management (`healthcare_state.py`)
- `PatientInfo` - Patient demographics and history
- `Symptom` - Structured symptom data
- `Diagnosis` - Differential diagnosis structure
- `TreatmentOption` - Treatment recommendations
- `DrugInteraction` - Drug interaction tracking
- `ClinicalState` - Main state TypedDict
- Helper functions for state manipulation

### ✅ LangSmith Configuration (`langsmith_config.py`)
- LangSmith client setup
- Evaluation dataset creation
- 5 clinical test cases:
  - CASE001: Upper respiratory infection (easy)
  - CASE002: Acute coronary syndrome (critical)
  - CASE003: Bacterial meningitis (critical)  
  - CASE004: Lung cancer workup (hard)
  - CASE005: Urinary tract infection (easy)
- Tracing decorators
- Feedback collection framework

### ✅ Orchestrator (`orchestrator.py`)
- Basic LangGraph workflow with 3 nodes:
  1. `analyze_case` - Initial case assessment
  2. `generate_todos` - Create analysis task list
  3. `safety_check` - Safety validation
- LLM integration with Claude Sonnet 4
- Automated safety alerts for:
  - Pediatric patients
  - Geriatric patients
  - Multiple chronic conditions
  - Critical cases

### ✅ Testing (`test_state.py`)
- Unit tests for all state models
- Tests for state management functions
- BMI calculation validation
- Pediatric/geriatric detection
- Safety alert and TODO tracking

## Verification Checklist

- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] API keys configured
- [ ] Tests pass (run `pytest`)
- [ ] Main demo runs successfully
- [ ] LangSmith dashboard shows traces
- [ ] Evaluation dataset created (5 cases)

## Troubleshooting

### ImportError: No module named 'langgraph'
```bash
pip install -r requirements.txt
```

### LANGSMITH_API_KEY not found
- Edit `.env` file and add your LangSmith API key
- Or set environment variable manually

### Tests failing
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Next Steps

After Phase 1 is working:

1. **Phase 2**: Implement symptom analysis agent
   - Medical literature search (PubMed)
   - Differential diagnosis generation
   - Red flag detection

2. **Phase 3**: Treatment planning agent
   - Clinical guidelines integration
   - Evidence-based recommendations
   - Treatment option ranking

3. **Phase 4**: Drug interaction checking
   - FDA API integration
   - Contraindication detection
   - Dosing calculations

## Success Criteria

Phase 1 is complete when:

- ✅ All files created
- ✅ Tests pass
- ✅ Main demo runs
- ✅ LangSmith tracing works
- ✅ Evaluation dataset has 5+ cases
- ✅ Basic workflow executes end-to-end

## Resources

- **Documentation**: See README.md
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangSmith**: https://smith.langchain.com/
- **Anthropic**: https://docs.anthropic.com/

---

**Phase 1 Status**: Implementation Complete ✅
**Next**: Move to Phase 2 - Symptom Analysis Agent
