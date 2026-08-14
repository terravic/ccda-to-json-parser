"""
Modular Section Parsers and Section Router for C-CDA documents.
"""

from typing import Any, Callable, Dict, Optional
import xml.etree.ElementTree as ET

from .allergies import parse_allergies_section
from .encounters import parse_encounters_section
from .generic_section import parse_generic_section
from .header import parse_header
from .immunizations import parse_immunizations_section
from .medications import parse_medications_section
from .problems import parse_problems_section
from .procedures import parse_procedures_section
from .results import parse_results_section
from .social_history import parse_social_history_section
from .vital_signs import parse_vital_signs_section
from ..utils.code_utils import parse_code
from ..utils.xml_utils import find_child, get_template_ids, get_text

# Mapping of known template IDs to section names
TEMPLATE_MAP: Dict[str, str] = {
    "2.16.840.1.113883.10.20.22.2.6": "allergies",
    "2.16.840.1.113883.10.20.22.2.6.1": "allergies",
    "2.16.840.1.113883.10.20.22.2.1": "medications",
    "2.16.840.1.113883.10.20.22.2.1.1": "medications",
    "2.16.840.1.113883.10.20.22.2.38": "medications_administered",
    "2.16.840.1.113883.10.20.22.2.5": "problems",
    "2.16.840.1.113883.10.20.22.2.5.1": "problems",
    "2.16.840.1.113883.10.20.22.2.2": "immunizations",
    "2.16.840.1.113883.10.20.22.2.2.1": "immunizations",
    "2.16.840.1.113883.10.20.22.2.4": "vital_signs",
    "2.16.840.1.113883.10.20.22.2.4.1": "vital_signs",
    "2.16.840.1.113883.10.20.22.2.3": "results",
    "2.16.840.1.113883.10.20.22.2.3.1": "results",
    "2.16.840.1.113883.10.20.22.2.22": "encounters",
    "2.16.840.1.113883.10.20.22.2.22.1": "encounters",
    "2.16.840.1.113883.10.20.22.2.7": "procedures",
    "2.16.840.1.113883.10.20.22.2.7.1": "procedures",
    "2.16.840.1.113883.10.20.22.2.17": "social_history",
    "2.16.840.1.113883.10.20.22.2.10": "plan_of_care",
    "2.16.840.1.113883.10.20.22.2.14": "functional_status",
    "2.16.840.1.113883.10.20.22.2.23": "medical_equipment",
    "2.16.840.1.113883.10.20.22.2.21": "advance_directives",
    "2.16.840.1.113883.10.20.22.2.8": "assessments",
    "2.16.840.1.113883.10.20.22.2.9": "assessment_and_plan",
    "2.16.840.1.113883.10.20.22.2.15": "family_history",
    "2.16.840.1.113883.10.20.22.2.18": "payers",
    "2.16.840.1.113883.10.20.22.2.41": "hospital_discharge_instructions",
    "2.16.840.1.113883.10.20.22.2.44": "hospital_course",
}

# Mapping of known LOINC codes to section names
LOINC_MAP: Dict[str, str] = {
    "48765-2": "allergies",
    "10160-0": "medications",
    "29549-3": "medications_administered",
    "10183-2": "discharge_medications",
    "11450-4": "problems",
    "11369-6": "immunizations",
    "8716-3": "vital_signs",
    "30954-2": "results",
    "18719-5": "results",
    "19146-0": "results",
    "26436-6": "results",
    "46240-8": "encounters",
    "47519-4": "procedures",
    "29762-2": "social_history",
    "18776-5": "plan_of_care",
    "47420-5": "functional_status",
    "46264-8": "medical_equipment",
    "42348-3": "advance_directives",
    "51848-0": "assessments",
    "51847-2": "assessment_and_plan",
    "10157-6": "family_history",
    "48768-6": "payers",
    "8648-8": "hospital_course",
    "69730-0": "hospital_discharge_instructions",
    "42344-2": "discharge_diet",
    "42349-1": "reason_for_referral",
    "10154-3": "chief_complaint",
    "29299-5": "reason_for_visit",
    "29545-1": "physical_exam",
    "10187-3": "review_of_systems",
    "61146-7": "goals",
}

# Parser function dispatch table
PARSER_FUNCTIONS: Dict[str, Callable[[ET.Element, Optional[Dict[str, str]]], Dict[str, Any]]] = {
    "allergies": parse_allergies_section,
    "medications": parse_medications_section,
    "medications_administered": parse_medications_section,
    "discharge_medications": parse_medications_section,
    "problems": parse_problems_section,
    "immunizations": parse_immunizations_section,
    "vital_signs": parse_vital_signs_section,
    "results": parse_results_section,
    "encounters": parse_encounters_section,
    "procedures": parse_procedures_section,
    "social_history": parse_social_history_section,
}


def identify_section_type(section_el: ET.Element) -> str:
    """
    Identifies the canonical section type string (e.g., 'allergies', 'medications')
    using template IDs, LOINC code, or title heuristics.
    """
    # 1. Match by templateId
    tids = get_template_ids(section_el)
    for tid in tids:
        raw_root = tid.split(":")[0] if ":" in tid else tid
        if raw_root in TEMPLATE_MAP:
            return TEMPLATE_MAP[raw_root]

    # 2. Match by LOINC / section code
    code_el = find_child(section_el, "code")
    code_dict = parse_code(code_el)
    if code_dict and code_dict.get("code") in LOINC_MAP:
        return LOINC_MAP[code_dict["code"]]

    # 3. Match by title heuristic
    title = (get_text(find_child(section_el, "title")) or "").lower()
    if "allerg" in title or "adverse" in title:
        return "allergies"
    if "medicat" in title or "medicine" in title or "prescription" in title or "drug" in title:
        if "discharge" in title:
            return "discharge_medications"
        if "admin" in title:
            return "medications_administered"
        return "medications"
    if "problem" in title or "condition" in title or "diagnosis" in title:
        return "problems"
    if "immuniz" in title or "vaccin" in title:
        return "immunizations"
    if "vital" in title:
        return "vital_signs"
    if "result" in title or "lab" in title or "diagnostic" in title:
        return "results"
    if "encounter" in title or "visit" in title:
        return "encounters"
    if "procedure" in title or "surger" in title or "operation" in title:
        return "procedures"
    if "social" in title or "smoking" in title or "tobacco" in title:
        return "social_history"
    if "plan of" in title or "care plan" in title or "treatment plan" in title:
        return "plan_of_care"
    if "hospital course" in title:
        return "hospital_course"
    if "chief complaint" in title:
        return "chief_complaint"
    if "referral" in title:
        return "reason_for_referral"
    if "discharge instruction" in title:
        return "hospital_discharge_instructions"
    if "assessment" in title:
        return "assessment_and_plan"

    # Fallback to normalized title slug or "generic"
    slug = "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")
    return slug or "generic_section"


def parse_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> tuple[str, Dict[str, Any]]:
    """
    Parses a section element using the appropriate specialized or generic parser.
    Returns (section_type_key, parsed_data_dict).
    """
    sec_type = identify_section_type(section_el)
    parser_fn = PARSER_FUNCTIONS.get(sec_type, parse_generic_section)
    parsed = parser_fn(section_el, ref_map)
    return sec_type, parsed
