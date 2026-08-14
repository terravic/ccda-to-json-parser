"""
Core C-CDA (Consolidated Clinical Document Architecture) to JSON Parser Engine.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
import xml.etree.ElementTree as ET

from .models import ParsedCCDA
from .sections import identify_section_type, parse_header, parse_section
from .utils.narrative_utils import build_id_reference_map
from .utils.xml_utils import (
    find_all_descendants,
    find_child,
    find_children,
    find_descendant,
    parse_xml,
)

logger = logging.getLogger(__name__)


class CCDAParser:
    """
    Parser engine that converts HL7 C-CDA XML documents into structured JSON format.
    Handles all C-CDA document types (CCD, Discharge Summary, Referral Note, Care Plan, etc.)
    and handles XML syntax variations (namespaces, null flavors, narrative references).
    """

    def __init__(self, strict: bool = False):
        """
        Args:
            strict: If True, raises exceptions on malformed sections; if False, catches and logs.
        """
        self.strict = strict

    def parse(self, xml_source: Union[str, bytes, ET.Element]) -> Dict[str, Any]:
        """
        Parses a C-CDA XML source (file path, raw XML string/bytes, or ElementTree root)
        into a structured dictionary matching the C-CDA JSON schema.
        """
        # Parse XML and strip namespaces
        root = parse_xml(xml_source, strip_ns=True)

        # Ensure it's a ClinicalDocument
        if root.tag.lower() != "clinicaldocument":
            # Sometimes wrapped in a root container or named differently
            found_doc = root.find(".//ClinicalDocument") or root.find(".//clinicaldocument")
            if found_doc is not None:
                root = found_doc
            elif not self.strict:
                logger.warning(f"Root element '{root.tag}' is not 'ClinicalDocument'. Attempting best-effort parse.")

        # Build reference lookup map from narrative IDs (e.g., #med1)
        ref_map = build_id_reference_map(root)

        # 1. Parse Header (Document Metadata & Patient Demographics)
        header_data = parse_header(root)
        patient_data = header_data.pop("patient", {})

        # 2. Locate Sections
        # Standard path: ClinicalDocument / component / structuredBody / component / section
        sections_dict: Dict[str, Any] = {}
        all_sections_list: List[Dict[str, Any]] = []

        # Find structuredBody
        structured_body = find_descendant(root, "component/structuredBody")
        section_elements: List[ET.Element] = []

        if structured_body is not None:
            for comp in find_children(structured_body, "component"):
                sec = find_child(comp, "section")
                if sec is not None:
                    section_elements.append(sec)
        else:
            # Fallback: search for any section elements
            section_elements = list(root.iter("section"))

        # 3. Parse each section
        for sec_el in section_elements:
            try:
                sec_type, parsed_section = parse_section(sec_el, ref_map)
                
                # Add section type to parsed section dict
                parsed_section["section_type"] = sec_type
                all_sections_list.append(parsed_section)

                # Store in sections_dict (group multiple sections of same type if present)
                if sec_type in sections_dict:
                    existing = sections_dict[sec_type]
                    if isinstance(existing, list):
                        existing.append(parsed_section)
                    else:
                        sections_dict[sec_type] = [existing, parsed_section]
                else:
                    sections_dict[sec_type] = parsed_section

            except Exception as e:
                logger.error(f"Error parsing section: {e}", exc_info=True)
                if self.strict:
                    raise
                # Fallback: record error in section
                error_sec = {
                    "section_type": "error",
                    "error": str(e),
                    "title": "Error Section",
                }
                all_sections_list.append(error_sec)

        # 4. Build Quick Clinical Summary
        summary = self._build_clinical_summary(patient_data, sections_dict)

        result = {
            "document_meta": header_data,
            "patient": patient_data,
            "summary": summary,
            "sections": sections_dict,
            "all_sections": all_sections_list,
        }

        return result

    def _build_clinical_summary(self, patient: Dict[str, Any], sections: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a high-level summary overview of the clinical document."""
        patient_name = ""
        if patient.get("name"):
            patient_name = patient["name"].get("full_name", "")
        
        dob = patient.get("birth_time")
        gender = ""
        if patient.get("gender"):
            gender = patient["gender"].get("display_name") or patient["gender"].get("code") or ""

        # Counts
        def get_entry_count(section_key: str) -> int:
            sec = sections.get(section_key)
            if not sec:
                return 0
            if isinstance(sec, list):
                return sum(len(s.get("entries", [])) for s in sec)
            return len(sec.get("entries", []))

        def get_results_count() -> int:
            sec = sections.get("results")
            if not sec:
                return 0
            if isinstance(sec, list):
                return sum(len(s.get("results", [])) for s in sec)
            return len(sec.get("results", []))

        def get_vitals_count() -> int:
            sec = sections.get("vital_signs")
            if not sec:
                return 0
            if isinstance(sec, list):
                return sum(len(s.get("measurements", [])) for s in sec)
            return len(sec.get("measurements", []))

        return {
            "patient_name": patient_name,
            "date_of_birth": dob,
            "gender": gender,
            "counts": {
                "allergies": get_entry_count("allergies"),
                "medications": get_entry_count("medications") + get_entry_count("discharge_medications"),
                "problems": get_entry_count("problems"),
                "immunizations": get_entry_count("immunizations"),
                "vital_signs": get_vitals_count(),
                "lab_results": get_results_count(),
                "encounters": get_entry_count("encounters"),
                "procedures": get_entry_count("procedures"),
            },
            "available_sections": list(sections.keys()),
        }


def parse_ccda(xml_source: Union[str, bytes, ET.Element], strict: bool = False) -> Dict[str, Any]:
    """Convenience function to parse C-CDA string/bytes or Element."""
    parser = CCDAParser(strict=strict)
    return parser.parse(xml_source)


def parse_ccda_file(file_path: str, strict: bool = False) -> Dict[str, Any]:
    """Convenience function to parse a C-CDA XML file from disk."""
    parser = CCDAParser(strict=strict)
    return parser.parse(file_path)
