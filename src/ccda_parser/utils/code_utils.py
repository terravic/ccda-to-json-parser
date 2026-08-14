"""
HL7 Coded Concept extraction and Code System OID mapping utilities.

Supports standard terminologies:
- SNOMED CT (2.16.840.1.113883.6.96)
- LOINC (2.16.840.1.113883.6.1)
- RxNorm (2.16.840.1.113883.6.88)
- ICD-10-CM (2.16.840.1.113883.6.90)
- ICD-9-CM (2.16.840.1.113883.6.103)
- CPT-4 (2.16.840.1.113883.6.12)
- CVX (2.16.840.1.113883.12.292)
- NDC (2.16.840.1.113883.6.69)
- NDF-RT (2.16.840.1.113883.6.89)
- UNII (2.16.840.1.113883.4.9)
- HL7 Administrative Gender (2.16.840.1.113883.5.1)
- HL7 ActCode / Confidentiality / NullFlavor
"""

from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

from .xml_utils import find_child, find_children, get_attr, get_null_flavor, get_text


# Standard OID to Code System Name mappings
KNOWN_CODE_SYSTEMS: Dict[str, str] = {
    "2.16.840.1.113883.6.96": "SNOMED CT",
    "2.16.840.1.113883.6.1": "LOINC",
    "2.16.840.1.113883.6.88": "RxNorm",
    "2.16.840.1.113883.6.90": "ICD-10-CM",
    "2.16.840.1.113883.6.4": "ICD-10-PCS",
    "2.16.840.1.113883.6.103": "ICD-9-CM",
    "2.16.840.1.113883.6.104": "ICD-9-PCS",
    "2.16.840.1.113883.6.12": "CPT-4",
    "2.16.840.1.113883.12.292": "CVX",
    "2.16.840.1.113883.6.69": "NDC",
    "2.16.840.1.113883.6.89": "NDF-RT",
    "2.16.840.1.113883.4.9": "UNII",
    "2.16.840.1.113883.5.1": "AdministrativeGender",
    "2.16.840.1.113883.5.25": "Confidentiality",
    "2.16.840.1.113883.5.83": "ObservationInterpretation",
    "2.16.840.1.113883.5.4": "ActCode",
    "2.16.840.1.113883.5.1008": "NullFlavor",
    "2.16.840.1.113883.6.238": "Race & Ethnicity - CDC",
    "2.16.840.1.113883.5.2": "MaritalStatus",
    "2.16.840.1.113883.5.60": "LanguageAbilityMode",
    "2.16.840.1.113883.5.61": "LanguageAbilityProficiency",
    "2.16.840.1.113883.5.111": "RoleCode",
    "2.16.840.1.113883.5.8": "ActReason",
    "2.16.840.1.113883.5.14": "ActStatus",
}


def parse_code(elem: Optional[ET.Element]) -> Optional[Dict[str, Any]]:
    """
    Parses an HL7 CD, CE, CV, CS, or SC coded element.
    Extracts code, displayName, codeSystem, codeSystemName, translations,
    and originalText reference.
    """
    if elem is None:
        return None

    null_flavor = get_null_flavor(elem)
    if null_flavor and not elem.attrib.get("code"):
        return {"null_flavor": null_flavor}

    code = get_attr(elem, "code")
    display_name = get_attr(elem, "displayName")
    code_system = get_attr(elem, "codeSystem")
    code_system_name = get_attr(elem, "codeSystemName")
    code_system_version = get_attr(elem, "codeSystemVersion")

    # If codeSystemName is missing, resolve from OID dictionary
    if code_system and not code_system_name:
        code_system_name = KNOWN_CODE_SYSTEMS.get(code_system)

    # Extract original text and reference
    orig_text_el = find_child(elem, "originalText")
    original_text = None
    reference_id = None
    if orig_text_el is not None:
        original_text = get_text(orig_text_el)
        ref_el = find_child(orig_text_el, "reference")
        if ref_el is not None:
            ref_val = get_attr(ref_el, "value")
            if ref_val:
                reference_id = ref_val.lstrip("#")

    # If display_name is missing, try original_text or tag inner text
    if not display_name and original_text:
        display_name = original_text

    # Extract translations (alternative codings)
    translations: List[Dict[str, Any]] = []
    for trans_el in find_children(elem, "translation"):
        trans_dict = parse_single_code(trans_el)
        if trans_dict:
            translations.append(trans_dict)

    result: Dict[str, Any] = {}
    if code is not None:
        result["code"] = code
    if display_name:
        result["display_name"] = display_name
    if code_system:
        result["code_system"] = code_system
    if code_system_name:
        result["code_system_name"] = code_system_name
    if code_system_version:
        result["code_system_version"] = code_system_version
    if original_text:
        result["original_text"] = original_text
    if reference_id:
        result["reference_id"] = reference_id
    if translations:
        result["translations"] = translations
    if null_flavor:
        result["null_flavor"] = null_flavor

    return result if result else None


def parse_single_code(elem: Optional[ET.Element]) -> Optional[Dict[str, Any]]:
    """Helper to parse a single code element without nested translations."""
    if elem is None:
        return None
    code = get_attr(elem, "code")
    display_name = get_attr(elem, "displayName")
    code_system = get_attr(elem, "codeSystem")
    code_system_name = get_attr(elem, "codeSystemName") or KNOWN_CODE_SYSTEMS.get(code_system or "")

    result: Dict[str, Any] = {}
    if code:
        result["code"] = code
    if display_name:
        result["display_name"] = display_name
    if code_system:
        result["code_system"] = code_system
    if code_system_name:
        result["code_system_name"] = code_system_name
    return result if result else None


def parse_value_element(elem: Optional[ET.Element]) -> Optional[Any]:
    """
    Parses an HL7 <value> element which can be:
    - PQ (Physical Quantity): value and unit (e.g. value="120" unit="mm[Hg]")
    - CD / CE (Coded): code, displayName, codeSystem
    - ST (String): text content
    - BL (Boolean): value="true"/"false"
    - INT (Integer): value="1"
    - IVL_PQ (Interval Physical Quantity): low, high
    """
    if elem is None:
        return None

    null_flavor = get_null_flavor(elem)
    if null_flavor and not elem.attrib.get("value") and not elem.attrib.get("code"):
        return {"null_flavor": null_flavor}

    xsi_type = get_attr(elem, "type") or elem.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type")

    # Check for Physical Quantity (PQ)
    val = get_attr(elem, "value")
    unit = get_attr(elem, "unit")
    if val is not None and unit is not None:
        return {
            "type": "PQ",
            "value": float(val) if is_number(val) else val,
            "unit": unit,
            "formatted": f"{val} {unit}".strip(),
        }

    # Check for Coded Value (CD / CE)
    code = get_attr(elem, "code")
    if code is not None:
        cd_data = parse_code(elem)
        if cd_data:
            cd_data["type"] = "CD"
            return cd_data

    # Check for string or boolean or int value attr
    if val is not None:
        if val.lower() in ("true", "false"):
            return {"type": "BL", "value": val.lower() == "true"}
        if is_number(val):
            num = float(val) if "." in val else int(val)
            return {"type": "NUM", "value": num}
        return {"type": "ST", "value": val}

    # Check for Interval Physical Quantity (IVL_PQ)
    low_el = find_child(elem, "low")
    high_el = find_child(elem, "high")
    if low_el is not None or high_el is not None:
        low_val = get_attr(low_el, "value") if low_el is not None else None
        low_unit = get_attr(low_el, "unit") if low_el is not None else None
        high_val = get_attr(high_el, "value") if high_el is not None else None
        high_unit = get_attr(high_el, "unit") if high_el is not None else None
        return {
            "type": "IVL_PQ",
            "low": {"value": float(low_val) if low_val and is_number(low_val) else low_val, "unit": low_unit} if low_val else None,
            "high": {"value": float(high_val) if high_val and is_number(high_val) else high_val, "unit": high_unit} if high_val else None,
        }

    # Fallback to inner text
    inner_text = get_text(elem)
    if inner_text:
        return {"type": "ST", "value": inner_text}

    return None


def is_number(s: str) -> bool:
    """Check if string is numeric (int or float)."""
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False
