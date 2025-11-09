"""
Tests for Phase 2 - Symptom Analysis Tools
"""

import pytest
from src.tools.symptom_tools import (
    generate_differential_diagnosis,
    detect_red_flags,
    EMERGENCY_RED_FLAGS
)
from src.tools.pubmed_search import (
    search_pubmed,
    format_citation,
    PubMedArticle
)


class TestDifferentialDiagnosis:
    """Tests for differential diagnosis generation"""
    
    def test_generate_diagnosis_basic(self):
        """Test basic differential diagnosis generation"""
        symptoms = ["fever", "cough", "fatigue"]
        result = generate_differential_diagnosis(symptoms, age=35, patient_sex="M")
        
        assert isinstance(result, list)
        assert len(result) >= 3  # Should generate at least 3 diagnoses
        
        # Check structure of first diagnosis
        first_dx = result[0]
        assert "condition" in first_dx
        assert "probability" in first_dx
        assert "reasoning" in first_dx
        
        # Probability should be between 0 and 1
        assert 0.0 <= first_dx["probability"] <= 1.0
    
    def test_diagnoses_ordered_by_probability(self):
        """Test that diagnoses are ordered from highest to lowest probability"""
        symptoms = ["chest pain", "shortness of breath"]
        result = generate_differential_diagnosis(symptoms, age=55, patient_sex="M")
        
        if len(result) > 1:
            # First diagnosis should have highest probability
            assert result[0]["probability"] >= result[1]["probability"]


class TestRedFlagDetection:
    """Tests for emergency red flag detection"""
    
    def test_cardiac_red_flag(self):
        """Test detection of cardiac emergencies"""
        symptoms = ["crushing chest pain", "radiating to left arm"]
        flags = detect_red_flags(symptoms, patient_age=55)
        
        assert len(flags) > 0
        assert any("CARDIAC" in flag for flag in flags)
    
    def test_neurologic_red_flag(self):
        """Test detection of neurologic emergencies"""
        symptoms = ["worst headache of life", "neck stiffness"]
        flags = detect_red_flags(symptoms, patient_age=30)
        
        assert len(flags) > 0
        assert any("NEUROLOGIC" in flag for flag in flags)
    
    def test_pediatric_red_flag(self):
        """Test pediatric-specific red flags"""
        symptoms = ["inconsolable crying", "lethargy"]
        flags = detect_red_flags(symptoms, patient_age=2)
        
        assert len(flags) > 0
        assert any("PEDIATRIC" in flag for flag in flags)
    
    def test_no_red_flags_routine_case(self):
        """Test that routine cases don't trigger red flags"""
        symptoms = ["mild headache", "fatigue"]
        flags = detect_red_flags(symptoms, patient_age=25)
        
        # Should not detect false positive red flags
        assert len(flags) == 0


class TestPubMedSearch:
    """Tests for PubMed literature search"""
    
    def test_search_pubmed_returns_results(self):
        """Test that PubMed search returns articles"""
        results = search_pubmed("hypertension treatment", max_results=3)
        
        assert isinstance(results, list)
        assert len(results) <= 3
        assert len(results) > 0
        
        # Check article structure
        first_article = results[0]
        assert hasattr(first_article, 'pmid')
        assert hasattr(first_article, 'title')
        assert hasattr(first_article, 'abstract')
        assert hasattr(first_article, 'journal')
        assert hasattr(first_article, 'year')
    
    def test_article_citation_format(self):
        """Test article citation formatting"""
        article = PubMedArticle(
            pmid="12345678",
            title="Test Article Title",
            abstract="Test abstract",
            journal="Test Journal",
            year="2024",
            authors=["Smith J", "Doe A"]
        )
        
        citation = format_citation(article)
        
        assert "Smith J" in citation
        assert "Test Article Title" in citation
        assert "Test Journal" in citation
        assert "2024" in citation
        assert "12345678" in citation


class TestEmergencyRedFlags:
    """Test the emergency red flag patterns dictionary"""
    
    def test_red_flag_categories_exist(self):
        """Test that all expected red flag categories exist"""
        expected_categories = ["cardiac", "neurologic", "respiratory", "gastrointestinal", "pediatric"]
        
        for category in expected_categories:
            assert category in EMERGENCY_RED_FLAGS
            assert isinstance(EMERGENCY_RED_FLAGS[category], list)
            assert len(EMERGENCY_RED_FLAGS[category]) > 0
    
    def test_cardiac_red_flags_comprehensive(self):
        """Test cardiac red flags are comprehensive"""
        cardiac_flags = EMERGENCY_RED_FLAGS["cardiac"]
        
        # Should include common cardiac emergency symptoms
        assert any("chest pain" in flag for flag in cardiac_flags)
        assert len(cardiac_flags) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
