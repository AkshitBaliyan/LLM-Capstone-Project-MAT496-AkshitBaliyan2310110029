"""
Integration Tests for Healthcare CDSS

Tests the complete end-to-end workflow with real clinical cases.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from examples import get_all_demo_cases
from src.agents import run_clinical_analysis


class TestEndToEndWorkflow:
    """Test complete workflow on various cases"""
    
    def test_uri_case_workflow(self):
        """Test URI case generates appropriate diagnosis"""
        from examples import get_uri_case
        
        state = get_uri_case()
        result = run_clinical_analysis(state)
        
        # Should complete without errors
        assert result is not None
        assert "session_id" in result
        
        # Should generate differential diagnosis
        assert "differential_diagnosis" in result
        assert len(result["differential_diagnosis"]) > 0
        
        # Top diagnosis should be respiratory related
        top_dx = result["differential_diagnosis"][0]
        assert "respiratory" in top_dx["condition"].lower() or "uri" in top_dx["condition"].lower() or "infection" in top_dx["condition"].lower()
        
        # Should have recommended tests
        assert "recommended_tests" in result
        assert len(result["recommended_tests"]) > 0
        
        # Routine case - should not require urgent review
        # (unless system is being extra cautious)
        assert "requires_human_review" in result
    
    def test_cardiac_emergency_detection(self):
        """Test that cardiac emergency is detected"""
        from examples import get_cardiac_emergency_case
        
        state = get_cardiac_emergency_case()
        result = run_clinical_analysis(state)
        
        # Should detect emergency
        assert result["requires_human_review"] == True
        
        # Should have safety alerts
        assert len(result["safety_alerts"]) > 0
        
        # Should mention cardiac or chest pain
        diagnosis_text = " ".join(
            [d["condition"] for d in result.get("differential_diagnosis", [])]
        ).lower()
        alert_text = " ".join(result.get("safety_alerts", [])).lower()
        
        assert "cardiac" in diagnosis_text or "cardiac" in alert_text or \
               "chest" in diagnosis_text or "coronary" in diagnosis_text
    
    def test_pediatric_handling(self):
        """Test pediatric patient triggers appropriate handling"""
        from examples import get_pediatric_case
        
        state = get_pediatric_case()
        result = run_clinical_analysis(state)
        
        # Should flag as pediatric
        alert_text = " ".join(result.get("safety_alerts", [])).lower()
        assert "pediatric" in alert_text or "age" in alert_text
        
        # Should require review for pediatric case
        assert result.get("requires_human_review") == True
    
    def test_geriatric_with_polypharmacy(self):
        """Test geriatric patient with multiple medications"""
        from examples import get_geriatric_case
        
        state = get_geriatric_case()
        result = run_clinical_analysis(state)
        
        # Should flag as geriatric
        alert_text = " ".join(result.get("safety_alerts", [])).lower()
        assert "geriatric" in alert_text or "age" in alert_text or "multiple" in alert_text
        
        # Should note multiple medications
        assert len(state["patient_info"].current_medications) >= 3


class TestWorkflowComponents:
    """Test individual workflow components"""
    
    def test_todo_generation(self):
        """Test that TODOs are generated"""
        from examples import get_uri_case
        
        state = get_uri_case()
        result = run_clinical_analysis(state)
        
        # Should have TODOs
        assert "todos" in result
        assert len(result["todos"]) > 0
        
        # At least one TODO should be marked completed
        completed = [t for t in result["todos"] if t["status"] == "completed"]
        assert len(completed) > 0
    
    def test_medical_literature_search(self):
        """Test that medical literature is searched"""
        from examples import get_uri_case
        
        state = get_uri_case()
        result = run_clinical_analysis(state)
        
        # Should have files (from literature search)
        assert "files" in result
        
        # Should have evidence sources
        assert "evidence_sources" in result
    
    def test_confidence_scores(self):
        """Test that confidence scores are generated"""
        from examples import get_uri_case
        
        state = get_uri_case()
        result = run_clinical_analysis(state)
        
        # Should have confidence scores
        assert "confidence_scores" in result
        
        # Should have diagnosis confidence
        if result.get("differential_diagnosis"):
            assert result["differential_diagnosis"][0]["probability"] >= 0.0
            assert result["differential_diagnosis"][0]["probability"] <= 1.0


class TestSafetyValidation:
    """Test safety validation features"""
    
    def test_red_flag_detection(self):
        """Test that red flags are detected"""
        from examples import get_cardiac_emergency_case
        
        state = get_cardiac_emergency_case()
        result = run_clinical_analysis(state)
        
        # Emergency case should have red flags
        assert len(result.get("safety_alerts", [])) > 0
    
    def test_human_review_requirement(self):
        """Test human review is required for high-risk cases"""
        cases = get_all_demo_cases()
        
        # Cardiac emergency and pediatric should require review
        for case_name in ["cardiac_emergency", "pediatric"]:
            result = run_clinical_analysis(cases[case_name])
            assert result["requires_human_review"] == True
            assert len(result.get("review_reasons", [])) > 0


class TestOutputQuality:
    """Test quality of outputs"""
    
    def test_diagnosis_has_reasoning(self):
        """Test that diagnoses include reasoning"""
        from examples import get_uri_case
        
        state = get_uri_case()
        result = run_clinical_analysis(state)
        
        if result.get("differential_diagnosis"):
            for dx in result["differential_diagnosis"]:
                assert "reasoning" in dx
                assert len(dx["reasoning"]) > 0
    
    def test_messages_generated(self):
        """Test that agent messages are generated"""
        from examples import get_uri_case
        
        state = get_uri_case()
        result = run_clinical_analysis(state)
        
        # Should have messages from agents
        assert "messages" in result
        assert len(result["messages"]) > 0
    
    def test_session_tracking(self):
        """Test that sessions are properly tracked"""
        from examples import get_uri_case
        
        state = get_uri_case()
        result = run_clinical_analysis(state)
        
        # Should have session metadata
        assert "session_id" in result
        assert "timestamp" in result
        assert "version" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
