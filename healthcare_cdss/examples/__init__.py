"""Examples package for Healthcare CDSS"""

from .clinical_cases import (
    get_uri_case,
    get_cardiac_emergency_case,
    get_pediatric_case,
    get_geriatric_case,
    get_all_demo_cases
)

__all__ = [
    "get_uri_case",
    "get_cardiac_emergency_case",
    "get_pediatric_case",
    "get_geriatric_case",
    "get_all_demo_cases"
]
