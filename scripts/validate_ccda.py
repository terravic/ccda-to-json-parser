#!/usr/bin/env python3
"""
C-CDA XML Structural and Conformance Validation Utility.
Checks C-CDA XML files for required HL7 CDA R2 / US Realm C-CDA header elements,
templateIds, patient demographics, and section structures.
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET

# Ensure src is in Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from ccda_parser.utils.xml_utils import (
    find_all_descendants,
    find_child,
    find_children,
    find_descendant,
    get_attr,
    get_template_ids,
    get_text,
    parse_xml,
)


def validate_ccda_file(xml_path: str) -> dict:
    errors = []
    warnings = []
    info = []

    if not os.path.exists(xml_path):
        return {"valid": False, "errors": [f"File not found: {xml_path}"], "warnings": [], "info": []}

    try:
        root = parse_xml(xml_path, strip_ns=True)
    except Exception as e:
        return {"valid": False, "errors": [f"XML Parsing Error: {e}"], "warnings": [], "info": []}

    if root.tag.lower() != "clinicaldocument":
        errors.append(f"Root tag must be 'ClinicalDocument', found '{root.tag}'")

    # Check US Realm Header Template ID (2.16.840.1.113883.10.20.22.1.1)
    doc_tids = get_template_ids(root)
    if not any("2.16.840.1.113883.10.20.22.1.1" in t for t in doc_tids):
        warnings.append("Missing standard US Realm Header templateId (2.16.840.1.113883.10.20.22.1.1)")
    else:
        info.append("Found US Realm Header templateId")

    # Document Type Code (LOINC)
    code_el = find_child(root, "code")
    if code_el is None or not get_attr(code_el, "code"):
        warnings.append("Missing or empty document type <code code='...'/> element in header")
    else:
        doc_code = get_attr(code_el, "code")
        disp_name = get_attr(code_el, "displayName") or ""
        info.append(f"Document Code: {doc_code} ({disp_name})")

    # Effective Time
    eff_time = find_child(root, "effectiveTime")
    if eff_time is None or not get_attr(eff_time, "value"):
        warnings.append("Missing or empty document <effectiveTime value='...'/> in header")

    # Patient demographics
    patient_role = find_descendant(root, "recordTarget/patientRole")
    if patient_role is None:
        errors.append("Missing required <recordTarget>/<patientRole> element")
    else:
        patient_el = find_child(patient_role, "patient")
        if patient_el is None:
            errors.append("Missing <patient> element inside patientRole")
        else:
            name_el = find_child(patient_el, "name")
            if name_el is None:
                warnings.append("Missing patient <name> element")
            gender_el = find_child(patient_el, "administrativeGenderCode")
            if gender_el is None or not get_attr(gender_el, "code"):
                warnings.append("Missing patient <administrativeGenderCode>")
            birth_el = find_child(patient_el, "birthTime")
            if birth_el is None or not get_attr(birth_el, "value"):
                warnings.append("Missing patient <birthTime>")

    # Structured Body & Sections
    structured_body = find_descendant(root, "component/structuredBody")
    if structured_body is None:
        warnings.append("Missing <structuredBody> in document body (might be non-XML body or narrative-only)")
    else:
        sections = list(structured_body.iter("section"))
        info.append(f"Found {len(sections)} clinical sections in structuredBody")
        for i, s in enumerate(sections, 1):
            title = get_text(find_child(s, "title")) or "(No Title)"
            s_code = get_attr(find_child(s, "code"), "code") or "No Code"
            entries = find_children(s, "entry")
            info.append(f"  Section {i}: '{title}' [Code: {s_code}] ({len(entries)} structured entries)")

    is_valid = len(errors) == 0
    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate C-CDA XML file conformance and structure.")
    parser.add_argument("file", help="Path to C-CDA XML file.")
    args = parser.parse_args()

    res = validate_ccda_file(args.file)
    print("\n" + "=" * 60)
    print(f" C-CDA VALIDATION REPORT: {args.file}")
    print("=" * 60)
    print(f" Status: {'✓ VALID C-CDA' if res['valid'] else '✗ INVALID / ERRORS FOUND'}\n")

    if res["errors"]:
        print(" ERRORS:")
        for e in res["errors"]:
            print(f"  [ERROR] {e}")
        print()

    if res["warnings"]:
        print(" WARNINGS:")
        for w in res["warnings"]:
            print(f"  [WARN]  {w}")
        print()

    if res["info"]:
        print(" DETAILS:")
        for inf in res["info"]:
            print(f"  [INFO]  {inf}")
        print()

    print("=" * 60 + "\n")
    sys.exit(0 if res["valid"] else 1)


if __name__ == "__main__":
    main()
