"""
Demo Script - Healthcare CDSS Examples

This script demonstrates the CDSS on multiple clinical cases:
1. Upper Respiratory Infection (routine)
2. Acute Coronary Syndrome (emergency)
3. Pediatric case
4. Geriatric case with multiple comorbidities
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from examples import get_all_demo_cases
from src.agents import run_clinical_analysis


def run_demo():
    """Run demo on all example cases"""
    
    print("\n" + "="*80)
    print("HEALTHCARE CDSS - COMPREHENSIVE DEMONSTRATION")
    print("="*80)
    print("\nThis demo runs the CDSS on 4 different clinical scenarios:")
    print("1. Upper Respiratory Infection (URI) - Routine case")
    print("2. Acute Coronary Syndrome - Emergency case")
    print("3. Pediatric Patient - Age-specific considerations")
    print("4. Geriatric Patient - Multiple comorbidities")
    print("\n" + "="*80 + "\n")
    
    # Get all demo cases
    cases = get_all_demo_cases()
    
    results = {}
    
    # Run each case
    for case_name, case_state in cases.items():
        print(f"\n{'█'*80}")
        print(f"  CASE: {case_name.upper().replace('_', ' ')}")
        print(f"{'█'*80}\n")
        
        try:
            result = run_clinical_analysis(case_state)
            results[case_name] = result
            
            # Brief summary
            print(f"\n{'─'*80}")
            print(f"CASE SUMMARY: {case_name}")
            print(f"{'─'*80}")
            
            if result.get("differential_diagnosis"):
                top_dx = result["differential_diagnosis"][0]
                print(f"Top Diagnosis: {top_dx['condition']}")
                print(f"Confidence: {top_dx['probability']*100:.1f}%")
            
            if result.get("safety_alerts"):
                print(f"\n⚠️  Safety Alerts: {len(result['safety_alerts'])}")
                for alert in result["safety_alerts"][:3]:
                    print(f"   • {alert}")
            
            if result.get("requires_human_review"):
                print(f"\n🔍 HUMAN REVIEW REQUIRED")
                for reason in result.get("review_reasons", []):
                    print(f"   • {reason}")
            
            print(f"{'─'*80}\n")
            
        except Exception as e:
            print(f"❌ Error processing {case_name}: {e}")
            results[case_name] = {"error": str(e)}
    
    # Final summary
    print(f"\n{'='*80}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nProcessed {len(results)} clinical cases")
    print(f"Emergency cases detected: {sum(1 for r in results.values() if r.get('requires_human_review'))}")
    print(f"\nAll cases traced in LangSmith for detailed analysis")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    run_demo()
