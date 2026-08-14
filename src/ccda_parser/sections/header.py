"""
C-CDA Header Parser: Patient Demographics, Document Metadata, Authors, Custodians, and Encounters.
"""

from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

from ..utils.code_utils import parse_code
from ..utils.date_utils import parse_effective_time, parse_hl7_date
from ..utils.xml_utils import (
    find_all_descendants,
    find_child,
    find_children,
    find_descendant,
    get_attr,
    get_ids,
    get_template_ids,
    get_text,
)


def parse_name(name_el: Optional[ET.Element]) -> Dict[str, Any]:
    """Parse an HL7 PN (Person Name) element."""
    if name_el is None:
        return {}

    given_names = [get_text(g) for g in find_children(name_el, "given") if get_text(g)]
    family_names = [get_text(f) for f in find_children(name_el, "family") if get_text(f)]
    prefixes = [get_text(p) for p in find_children(name_el, "prefix") if get_text(p)]
    suffixes = [get_text(s) for s in find_children(name_el, "suffix") if get_text(s)]

    first_name = given_names[0] if given_names else ""
    middle_names = given_names[1:] if len(given_names) > 1 else []
    last_name = family_names[0] if family_names else ""

    parts = []
    if prefixes:
        parts.extend(prefixes)
    if given_names:
        parts.extend(given_names)
    if family_names:
        parts.extend(family_names)
    if suffixes:
        parts.extend(suffixes)

    full_name = " ".join(parts) if parts else get_text(name_el)

    result: Dict[str, Any] = {
        "full_name": full_name,
        "first_name": first_name,
        "middle_names": middle_names,
        "last_name": last_name,
        "prefixes": prefixes,
        "suffixes": suffixes,
    }
    use = get_attr(name_el, "use")
    if use:
        result["use"] = use

    return result


def parse_address(addr_el: Optional[ET.Element]) -> Dict[str, Any]:
    """Parse an HL7 AD (Address) element."""
    if addr_el is None:
        return {}

    street_lines = [get_text(s) for s in find_children(addr_el, "streetAddressLine") if get_text(s)]
    city = get_text(find_child(addr_el, "city"))
    state = get_text(find_child(addr_el, "state"))
    postal_code = get_text(find_child(addr_el, "postalCode"))
    country = get_text(find_child(addr_el, "country"))
    use = get_attr(addr_el, "use")

    parts = []
    if street_lines:
        parts.append(", ".join(street_lines))
    if city:
        parts.append(city)
    if state:
        parts.append(f"{state} {postal_code}".strip() if postal_code else state)
    elif postal_code:
        parts.append(postal_code)
    if country:
        parts.append(country)

    return {
        "street_address_lines": street_lines,
        "city": city or None,
        "state": state or None,
        "postal_code": postal_code or None,
        "country": country or None,
        "use": use or None,
        "formatted": ", ".join(parts) if parts else None,
    }


def parse_telecom(telecom_el: Optional[ET.Element]) -> Dict[str, Any]:
    """Parse an HL7 TEL (Telecom) element."""
    if telecom_el is None:
        return {}

    val = get_attr(telecom_el, "value", "") or ""
    use = get_attr(telecom_el, "use")

    # Clean prefix like tel:, mailto:
    system = None
    clean_val = val
    if ":" in val:
        system, clean_val = val.split(":", 1)

    return {
        "system": system,
        "value": clean_val,
        "raw_value": val,
        "use": use,
    }


def parse_patient_demographics(root: ET.Element) -> Dict[str, Any]:
    """Extract patient demographics from recordTarget/patientRole."""
    record_target = find_child(root, "recordTarget")
    if record_target is None:
        return {}

    patient_role = find_child(record_target, "patientRole")
    if patient_role is None:
        return {}

    patient_el = find_child(patient_role, "patient")

    # IDs (MRN, SSN, etc.)
    ids = get_ids(patient_role)

    # Addresses
    addresses = [parse_address(a) for a in find_children(patient_role, "addr")]

    # Telecoms
    telecoms = [parse_telecom(t) for t in find_children(patient_role, "telecom")]

    demographics: Dict[str, Any] = {
        "ids": ids,
        "addresses": addresses,
        "telecoms": telecoms,
    }

    if patient_el is not None:
        # Names
        name_elements = find_children(patient_el, "name")
        names = [parse_name(n) for n in name_elements]
        demographics["name"] = names[0] if names else None
        demographics["names"] = names

        # Gender
        gender_el = find_child(patient_el, "administrativeGenderCode")
        demographics["gender"] = parse_code(gender_el)

        # Date of Birth
        birth_el = find_child(patient_el, "birthTime")
        demographics["birth_time"] = parse_hl7_date(get_attr(birth_el, "value")) if birth_el is not None else None

        # Marital Status
        marital_el = find_child(patient_el, "maritalStatusCode")
        demographics["marital_status"] = parse_code(marital_el)

        # Race (including sdtc extensions)
        races = []
        for race_el in find_children(patient_el, "raceCode"):
            rc = parse_code(race_el)
            if rc:
                races.append(rc)
        demographics["race"] = races[0] if races else None
        demographics["races"] = races

        # Ethnicity (including sdtc extensions)
        ethnicities = []
        for eth_el in find_children(patient_el, "ethnicGroupCode"):
            ec = parse_code(eth_el)
            if ec:
                ethnicities.append(ec)
        demographics["ethnicity"] = ethnicities[0] if ethnicities else None
        demographics["ethnicities"] = ethnicities

        # Language communication
        languages = []
        for lang_el in find_children(patient_el, "languageCommunication"):
            lang_code_el = find_child(lang_el, "languageCode")
            mode_el = find_child(lang_el, "modeCode")
            pref_el = find_child(lang_el, "preferenceInd")
            prof_el = find_child(lang_el, "proficiencyLevelCode")

            languages.append({
                "language": get_attr(lang_code_el, "code"),
                "mode": parse_code(mode_el),
                "preferred": get_attr(pref_el, "value") == "true" if pref_el is not None else False,
                "proficiency": parse_code(prof_el),
            })
        demographics["languages"] = languages

        # Guardians
        guardians = []
        for guard_el in find_children(patient_el, "guardian"):
            guard_person = find_child(guard_el, "guardianPerson")
            guard_name = parse_name(find_child(guard_person, "name")) if guard_person is not None else None
            guard_addr = [parse_address(a) for a in find_children(guard_el, "addr")]
            guard_tele = [parse_telecom(t) for t in find_children(guard_el, "telecom")]
            guard_code = parse_code(find_child(guard_el, "code"))

            guardians.append({
                "relationship": guard_code,
                "name": guard_name,
                "addresses": guard_addr,
                "telecoms": guard_tele,
            })
        if guardians:
            demographics["guardians"] = guardians

    # Provider / Organization
    org_el = find_child(patient_role, "providerOrganization")
    if org_el is not None:
        org_name = get_text(find_child(org_el, "name"))
        org_addr = [parse_address(a) for a in find_children(org_el, "addr")]
        org_tele = [parse_telecom(t) for t in find_children(org_el, "telecom")]
        org_ids = get_ids(org_el)
        demographics["provider_organization"] = {
            "name": org_name or None,
            "ids": org_ids,
            "addresses": org_addr,
            "telecoms": org_tele,
        }

    return demographics


def parse_authors(root: ET.Element) -> List[Dict[str, Any]]:
    """Extract authors from C-CDA header."""
    authors = []
    for author_el in find_children(root, "author"):
        time_el = find_child(author_el, "time")
        assigned_el = find_child(author_el, "assignedAuthor")
        if assigned_el is None:
            continue

        person_el = find_child(assigned_el, "assignedPerson")
        org_el = find_child(assigned_el, "representedOrganization")

        author_data: Dict[str, Any] = {
            "time": parse_hl7_date(get_attr(time_el, "value")) if time_el is not None else None,
            "ids": get_ids(assigned_el),
            "code": parse_code(find_child(assigned_el, "code")),
            "person": parse_name(find_child(person_el, "name")) if person_el is not None else None,
            "organization": {
                "name": get_text(find_child(org_el, "name")) if org_el is not None else None,
                "ids": get_ids(org_el) if org_el is not None else [],
                "addresses": [parse_address(a) for a in find_children(org_el, "addr")] if org_el is not None else [],
                "telecoms": [parse_telecom(t) for t in find_children(org_el, "telecom")] if org_el is not None else [],
            } if org_el is not None else None,
            "addresses": [parse_address(a) for a in find_children(assigned_el, "addr")],
            "telecoms": [parse_telecom(t) for t in find_children(assigned_el, "telecom")],
        }
        authors.append(author_data)
    return authors


def parse_custodian(root: ET.Element) -> Optional[Dict[str, Any]]:
    """Extract custodian organization from C-CDA header."""
    cust_el = find_child(root, "custodian")
    if cust_el is None:
        return None

    assigned_el = find_child(cust_el, "assignedCustodian")
    if assigned_el is None:
        return None

    rep_el = find_child(assigned_el, "representedCustodianOrganization")
    if rep_el is None:
        return None

    return {
        "name": get_text(find_child(rep_el, "name")) or None,
        "ids": get_ids(rep_el),
        "telecom": parse_telecom(find_child(rep_el, "telecom")),
        "address": parse_address(find_child(rep_el, "addr")),
    }


def parse_encompassing_encounter(root: ET.Element) -> Optional[Dict[str, Any]]:
    """Extract encompassingEncounter from componentOf."""
    comp_of = find_child(root, "componentOf")
    if comp_of is None:
        return None

    enc_el = find_child(comp_of, "encompassingEncounter")
    if enc_el is None:
        return None

    time_el = find_child(enc_el, "effectiveTime")
    code_el = find_child(enc_el, "code")
    discharge_el = find_child(enc_el, "dischargeDispositionCode")

    location_el = find_descendant(enc_el, "location/healthCareFacility/location")
    loc_name = get_text(find_child(location_el, "name")) if location_el is not None else None

    resp_party = find_descendant(enc_el, "responsibleParty/assignedEntity/assignedPerson/name")

    return {
        "ids": get_ids(enc_el),
        "code": parse_code(code_el),
        "effective_time": parse_effective_time(time_el),
        "discharge_disposition": parse_code(discharge_el),
        "location_name": loc_name,
        "responsible_party": parse_name(resp_party) if resp_party is not None else None,
    }


def parse_header(root: ET.Element) -> Dict[str, Any]:
    """Parse complete C-CDA Header metadata."""
    title = get_text(find_child(root, "title"))
    doc_id = get_ids(root)
    effective_time = parse_hl7_date(get_attr(find_child(root, "effectiveTime"), "value"))
    doc_code = parse_code(find_child(root, "code"))
    confidentiality = parse_code(find_child(root, "confidentialityCode"))
    language = get_attr(find_child(root, "languageCode"), "code")
    set_id = get_ids(find_child(root, "setId")) if find_child(root, "setId") is not None else []
    version_num = get_attr(find_child(root, "versionNumber"), "value")
    template_ids = get_template_ids(root)

    return {
        "document_id": doc_id[0] if doc_id else None,
        "document_type": doc_code,
        "title": title or (doc_code.get("display_name") if doc_code else "Clinical Document"),
        "effective_time": effective_time,
        "confidentiality": confidentiality,
        "language": language,
        "set_id": set_id[0] if set_id else None,
        "version_number": version_num,
        "template_ids": template_ids,
        "patient": parse_patient_demographics(root),
        "authors": parse_authors(root),
        "custodian": parse_custodian(root),
        "encompassing_encounter": parse_encompassing_encounter(root),
    }
