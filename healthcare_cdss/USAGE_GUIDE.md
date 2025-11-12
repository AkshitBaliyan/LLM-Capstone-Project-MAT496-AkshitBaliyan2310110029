# Healthcare CDSS - Usage Guide

## Quick Start

### Basic Usage

```python
from src.state import PatientInfo, Symptom, create_initial_state
from src.agents import run_clinical_analysis

# Create patient
patient = PatientInfo(
    patient_id="P001",
    age=45,
    sex="M",
    weight_kg=80.0,
    height_cm=175.0,
    allergies=["Penicillin"],
    current_medications=["Lisinopril"],
    chronic_conditions=["Hypertension"]
)

# Define symptoms
symptoms = [
    Symptom(
        description="fever",
        severity="moderate",
        onset="3 days ago",
        duration="ongoing"
    ),
    Symptom(
        description="cough",
        severity="moderate",
        onset="3 days ago",
        duration="ongoing"
    )
]

# Create initial state
state = create_initial_state(
    patient_info=patient,
    chief_complaint="Fever and cough",
    symptoms=symptoms,
    vital_signs={"temperature": 38.2, "heart_rate": 88}
)

# Run analysis
result = run_clinical_analysis(state)

# Access results
print(result["differential_diagnosis"])
print(result["recommended_tests"])
print(result["safety_alerts"])
```

## Example Cases

### Run Pre-Built Examples

```bash
python demo.py
```

This runs 4 example cases:
- Upper Respiratory Infection
- Cardiac Emergency
- Pediatric Case
- Geriatric Case

### Use Individual Examples

```python
from examples import get_uri_case, get_cardiac_emergency_case
from src.agents import run_clinical_analysis

# Run URI case
uri_state = get_uri_case()
result = run_clinical_analysis(uri_state)

# Run cardiac emergency
cardiac_state = get_cardiac_emergency_case()
result = run_clinical_analysis(cardiac_state)
```

## Understanding the Output

### Differential Diagnosis
```python
result["differential_diagnosis"]
# [
#   {
#     "condition": "Upper Respiratory Infection",
#     "probability": 0.85,
#     "reasoning": "Classic symptoms of...",
#     "typical_symptoms": ["fever", "cough", ...],
#     "red_flags": [],
#     "icd10_code": "J06.9"
#   },
#   ...
# ]
```

### Safety Alerts
```python
result["safety_alerts"]
# ["PEDIATRIC PATIENT (Age: 8) - Age-appropriate dosing required"]
```

### Human Review Flags
```python
result["requires_human_review"]  # True/False
result["review_reasons"]  # ["Emergency condition detected", ...]
```

### Medical Literature
```python
result["files"]  # Dictionary of stored articles
# {
#   "pubmed_12345678.md": "Full article content...",
#   ...
# }

result["evidence_sources"]  # List of citations
# ["Smith et al. Journal. 2024. PMID: 12345678", ...]
```

## Common Patterns

### Check for Emergencies

```python
result = run_clinical_analysis(state)

if result["requires_human_review"]:
    print("⚠️ URGENT: Human review required")
    for reason in result["review_reasons"]:
        print(f"  - {reason}")
    
    # Check for specific red flags
    for alert in result["safety_alerts"]:
        if "CARDIAC" in alert or "EMERGENCY" in alert:
            print(f"🚨 {alert}")
```

### Access Top Diagnosis

```python
if result["differential_diagnosis"]:
    top_dx = result["differential_diagnosis"][0]
    
    print(f"Top Diagnosis: {top_dx['condition']}")
    print(f"Confidence: {top_dx['probability']*100:.1f}%")
    print(f"Reasoning: {top_dx['reasoning']}")
    
    # Get recommended tests
    print(f"\nRecommended Tests:")
    for test in result["recommended_tests"]:
        print(f"  • {test}")
```

### Review Medical Evidence

```python
# List all stored articles
for filename in result["files"].keys():
    if filename.startswith("pubmed_"):
        print(f"Article: {filename}")

# Read specific article
article_content = result["files"]["pubmed_12345678.md"]
print(article_content)
```

## LangSmith Integration

All workflows are automatically traced in LangSmith:

1. Go to https://smith.langchain.com/
2. Navigate to project: `healthcare-cdss`
3. View execution traces with full details

### View Specific Session

```python
session_id = result["session_id"]
print(f"View in LangSmith: https://smith.langchain.com/o/.../p/healthcare-cdss/r/{session_id}")
```

## Advanced Usage

### Custom Workflow

```python
from src.agents import create_clinical_workflow

# Get compiled workflow
workflow = create_clinical_workflow()

# Run with custom config
config = {"recursion_limit": 50}
result = workflow.invoke(state, config=config)
```

### Access Individual Agents

```python
from src.agents import symptom_analyzer_node, literature_research_node

# Run symptom analysis only
analyzed_state = symptom_analyzer_node(state)

# Run literature research
researched_state = literature_research_node(analyzed_state)
```

### Use Individual Tools

```python
from src.tools import generate_differential_diagnosis, search_pubmed

# Generate diagnosis standalone
diagnoses = generate_differential_diagnosis(
    symptoms=["fever", "cough"],
    patient_age=35,
    patient_sex="M"
)

# Search PubMed
articles = search_pubmed("upper respiratory infection", max_results=5)
```

## Troubleshooting

### No API Keys
```
Error: ANTHROPIC_API_KEY not found
```
Solution: Create `.env` file with your API keys

### Import Errors
```
ImportError: No module named 'langgraph'
```
Solution: `pip install -r requirements.txt`

### LangSmith Not Tracing
Check `.env` file:
```
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=your_key_here
```

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_symptom_analysis.py -v
```

## Best Practices

1. **Always validate input**: Use Pydantic models for type safety
2. **Check safety alerts**: Never ignore requires_human_review flag
3. **Review evidence**: Check evidence_sources for decision support
4. **Monitor in LangSmith**: Track performance and quality
5. **Handle errors**: Wrap analysis in try-except blocks

## More Information

- Full documentation: `README.md`
- Setup guide: `SETUP_GUIDE.md`
- Implementation details: See source code documentation
- Example cases: `examples/clinical_cases.py`
