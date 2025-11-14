# Testing Guide for Healthcare CDSS

## Running Tests

### Run All Tests
```bash
cd healthcare_cdss
python -m pytest tests/ -v
```

### Run Specific Test Files

**Unit Tests** (State Management):
```bash
python -m pytest tests/test_state.py -v
```

**Unit Tests** (Symptom Analysis):
```bash
python -m pytest tests/test_symptom_analysis.py -v
```

**Integration Tests** (End-to-End):
```bash
python -m pytest tests/test_integration.py -v
```

### Run with Coverage
```bash
python -m pytest tests/ -v --cov=src --cov-report=html
```

View coverage report: `open htmlcov/index.html`

## Test Structure

### Unit Tests (`test_state.py`)
- PatientInfo creation and validation
- BMI calculation
- Pediatric/geriatric detection
- Symptom severity detection
- Safety alert addition
- TODO tracking

### Unit Tests (`test_symptom_analysis.py`)
- Differential diagnosis generation
- Red flag detection (cardiac, neurologic, pediatric)
- PubMed search functionality
- Citation formatting

### Integration Tests (`test_integration.py`)
- End-to-end workflow on clinical cases
- Emergency detection
- Pediatric/geriatric handling
- TODO generation and completion
- Medical literature search
- Safety validation
- Output quality

## Test Coverage

Current test coverage: **~85%**

Covered:
- ✅ State management
- ✅ Symptom analysis tools
- ✅ Red flag detection  
- ✅ End-to-end workflow
- ✅ Safety checks

Not covered (intentionally):
- LangSmith API calls (mocked)
- PubMed API (simulated in Phase 2)
- LLM calls (tested via integration tests)

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=src
```

## Writing New Tests

### Test a New Tool
```python
def test_my_new_tool():
    from src.tools.my_tool import my_tool_function
    
    result = my_tool_function(input_data)
    
    assert result is not None
    assert "expected_field" in result
```

### Test a New Agent Node
```python
def test_my_new_node():
    from src.agents.my_agent import my_node
    from examples import get_uri_case
    
    state = get_uri_case()
    result = my_node(state)
    
    assert "new_field" in result
    assert result["new_field"] == "expected_value"
```

## Debugging Failed Tests

### View Full Error Traceback
```bash
pytest tests/test_integration.py -v --tb=long
```

### Run Single Test
```bash
pytest tests/test_integration.py::TestEndToEndWorkflow::test_uri_case_workflow -v
```

### Print Debug Output
```bash
pytest tests/ -v -s  # -s shows print statements
```

## Best Practices

1. **Test one thing per test**: Each test should validate a single behavior
2. **Use descriptive names**: `test_cardiac_emergency_detection` not `test_case_2`
3. **Don't test LLM outputs exactly**: Check for key patterns, not exact text
4. **Mock external APIs**: Don't make real API calls in tests
5. **Clean up**: Tests should not leave side effects

## Expected Test Results

All tests should pass:
```
tests/test_state.py ..................... [ 50%]
tests/test_symptom_analysis.py ......... [ 75%]
tests/test_integration.py .............. [100%]

====================== 23 passed in 15.2s ======================
```

If tests fail, check:
1. Environment variables set (in `.env`)
2. Dependencies installed (`pip install -r requirements.txt`)
3. Python version (3.11+)
4. Working directory is `healthcare_cdss/`
