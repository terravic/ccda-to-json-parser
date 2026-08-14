"""
Immunizations Section Parser.
TemplateIds: 2.16.840.1.113883.10.20.22.2.2, 2.16.840.1.113883.10.20.22.2.2.1
LOINC: 11369-6
"""

from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

from ..utils.code_utils import parse_code, parse_value_element
from ..utils.date_utils import parse_effective_time
from ..utils.narrative_utils import (
    extract_narrative_text,
    parse_narrative_tables,
)
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


def parse_immunizations_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Parse C-CDA Immunizations Section."""
    title = get_text(find_child(section_el, "title")) or "Immunizations"
    text_el = find_child(section_el, "text")
    narrative = extract_narrative_text(text_el)
    tables = parse_narrative_tables(text_el)
    code = parse_code(find_child(section_el, "code"))
    template_ids = get_template_ids(section_el)

    entries: List[Dict[str, Any]] = []

    for entry_el in find_children(section_el, "entry"):
        sub_adm = find_child(entry_el, "substanceAdministration")
        if sub_adm is None:
            continue

        imm_ids = get_ids(sub_adm)
        status_code = get_attr(find_child(sub_adm, "statusCode"), "code")
        negation_ind = get_attr(sub_adm, "negationInd") == "true"
        date_administered = parse_effective_time(find_child(sub_adm, "effectiveTime"))
        route = parse_code(find_child(sub_adm, "routeCode"))
        site = parse_code(find_child(sub_adm, "approachSiteCode"))

        # Dose
        dose_el = find_child(sub_adm, "doseQuantity")
        dose = None
        if dose_el is not None:
            d_val = get_attr(dose_el, "value")
            d_unit = get_attr(dose_el, "unit")
            dose = {
                "value": float(d_val) if d_val and d_val.replace(".", "", 1).isdigit() else d_val,
                "unit": d_unit,
                "formatted": f"{d_val} {d_unit}".strip() if d_val else None,
            }

        # Vaccine product
        vaccine = None
        lot_number = None
        manufacturer = None

        consumable = find_child(sub_adm, "consumable")
        if consumable is not None:
            manuf_prod = find_child(consumable, "manufacturedProduct")
            if manuf_prod is not None:
                manuf_mat = find_child(manuf_prod, "manufacturedMaterial")
                if manuf_mat is not None:
                    vaccine = parse_code(find_child(manuf_mat, "code"))
                    lot_el = find_child(manuf_mat, "lotNumberText")
                    if lot_el is not None:
                        lot_number = get_text(lot_el)

                manuf_org = find_child(manuf_prod, "manufacturerOrganization")
                if manuf_org is not None:
                    manufacturer = get_text(find_child(manuf_org, "name"))

        if vaccine and not vaccine.get("display_name") and vaccine.get("reference_id") and ref_map:
            vaccine["display_name"] = ref_map.get(vaccine["reference_id"])

        # Refusal reason if refused / negated
        refusal_reason = None
        for rel in find_children(sub_adm, "entryRelationship"):
            obs = find_child(rel, "observation")
            if obs is not None:
                obs_code = parse_code(find_child(obs, "code"))
                if obs_code and obs_code.get("code") in ("PATOBJ", "IMMUNIZ", "refusal"):
                    refusal_reason = parse_value_element(find_child(obs, "value"))

        # Performer
        performer = None
        perf_el = find_child(sub_adm, "performer")
        if perf_el is not None:
            assign_el = find_child(perf_el, "assignedEntity")
            if assign_el is not None:
                person = find_child(assign_el, "assignedPerson")
                if person is not None:
                    performer = {"name": get_text(find_child(person, "name"))}

        entries.append({
            "vaccine": vaccine,
            "date": date_administered,
            "status": status_code,
            "negation": negation_ind,
            "refusal_reason": refusal_reason,
            "dose": dose,
            "route": route,
            "site": site,
            "lot_number": lot_number,
            "manufacturer": manufacturer,
            "performer": performer,
            "ids": imm_ids,
        })

    return {
        "title": title,
        "code": code,
        "template_ids": template_ids,
        "narrative": narrative,
        "tables": tables,
        "entries": entries,
    }
