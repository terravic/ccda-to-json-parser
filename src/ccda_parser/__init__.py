"""
C-CDA (Consolidated Clinical Document Architecture) to JSON Parser.

Converts HL7 C-CDA XML clinical documents (CCD, Discharge Summaries,
Consultation Notes, Care Plans, etc.) into clean, structured JSON format.
"""

from .models import CodedConcept, ParsedCCDA, PatientDemographics
from .parser import CCDAParser, parse_ccda, parse_ccda_file

__version__ = "1.0.0"
__all__ = [
    "CCDAParser",
    "parse_ccda",
    "parse_ccda_file",
    "ParsedCCDA",
    "PatientDemographics",
    "CodedConcept",
]
