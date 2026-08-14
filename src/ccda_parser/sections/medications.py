"""
Medications Section Parser.
TemplateIds: 2.16.840.1.113883.10.20.22.2.1, 2.16.840.1.113883.10.20.22.2.1.1, 2.16.840.1.113883.10.20.22.2.38
LOINC: 10160-0, 29549-3, 10183-2
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


def parse_medications_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Parse C-CDA Medications Section (including Active, Administered, Discharge medications)."""
    title = get_text(find_child(section_el, "title")) or "Medications"
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

        med_ids = get_ids(sub_adm)
        status_code = get_attr(find_child(sub_adm, "statusCode"), "code")

        # Effective times: Can have multiple effectiveTimes (one for date range, one for frequency/pivl)
        effective_times = []
        schedule = None
        date_range = None

        for eff_time in find_children(sub_adm, "effectiveTime"):
            parsed_eff = parse_effective_time(eff_time)
            if not parsed_eff:
                continue
            xsi_type = get_attr(eff_time, "type") or ""
            if "PIVL" in xsi_type or (isinstance(parsed_eff, dict) and "period" in parsed_eff):
                schedule = parsed_eff
            elif isinstance(parsed_eff, dict) and ("low" in parsed_eff or "high" in parsed_eff):
                date_range = parsed_eff
            else:
                effective_times.append(parsed_eff)

        # Route
        route = parse_code(find_child(sub_adm, "routeCode"))

        # Dose Quantity
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

        # Rate Quantity
        rate_el = find_child(sub_adm, "rateQuantity")
        rate = None
        if rate_el is not None:
            r_val = get_attr(rate_el, "value")
            r_unit = get_attr(rate_el, "unit")
            rate = {
                "value": float(r_val) if r_val and r_val.replace(".", "", 1).isdigit() else r_val,
                "unit": r_unit,
                "formatted": f"{r_val} {r_unit}".strip() if r_val else None,
            }

        # Consumable / Medication product
        medication = None
        lot_number = None
        manufacturer = None

        consumable = find_child(sub_adm, "consumable")
        if consumable is not None:
            manuf_prod = find_child(consumable, "manufacturedProduct")
            if manuf_prod is not None:
                manuf_mat = find_child(manuf_prod, "manufacturedMaterial")
                if manuf_mat is not None:
                    medication = parse_code(find_child(manuf_mat, "code"))
                    lot_el = find_child(manuf_mat, "lotNumberText")
                    if lot_el is not None:
                        lot_number = get_text(lot_el)

                manuf_org = find_child(manuf_prod, "manufacturerOrganization")
                if manuf_org is not None:
                    manufacturer = get_text(find_child(manuf_org, "name"))

        # Resolve display name from ref_map if needed
        if medication and not medication.get("display_name") and medication.get("reference_id") and ref_map:
            medication["display_name"] = ref_map.get(medication["reference_id"])

        # Indication & Instructions from entryRelationship
        indication = None
        instructions = None
        precondition = None

        # Check preconditions (e.g. PRN / As needed)
        for pre in find_children(sub_adm, "precondition"):
            crit = find_child(pre, "criterion")
            if crit is not None:
                crit_code = parse_code(find_child(crit, "code"))
                crit_val = parse_value_element(find_child(crit, "value"))
                precondition = {
                    "code": crit_code,
                    "value": crit_val,
                    "is_prn": True,
                }

        for rel in find_children(sub_adm, "entryRelationship"):
            # Indication Observation (2.16.840.1.113883.10.20.22.4.19)
            obs = find_child(rel, "observation")
            if obs is not None:
                ind_val = parse_value_element(find_child(obs, "value"))
                if ind_val:
                    indication = ind_val

            # Patient Instruction Act (2.16.840.1.113883.10.20.22.4.20)
            act = find_child(rel, "act")
            if act is not None:
                inst_text_el = find_child(act, "text")
                if inst_text_el is not None:
                    instructions = get_text(inst_text_el)
                    ref_el = find_child(inst_text_el, "reference")
                    if ref_el is not None and ref_map:
                        ref_val = get_attr(ref_el, "value", "").lstrip("#")
                        if ref_val in ref_map:
                            instructions = ref_map[ref_val]

        # Performer / Prescriber
        performer = None
        perf_el = find_child(sub_adm, "performer")
        if perf_el is not None:
            assign_el = find_child(perf_el, "assignedEntity")
            if assign_el is not None:
                person = find_child(assign_el, "assignedPerson")
                if person is not None:
                    p_name = get_text(find_child(person, "name"))
                    if p_name:
                        performer = {"name": p_name}

        entries.append({
            "medication": medication,
            "status": status_code,
            "dose": dose,
            "rate": rate,
            "route": route,
            "schedule": schedule,
            "date_range": date_range,
            "effective_times": effective_times if not date_range and not schedule else None,
            "indication": indication,
            "instructions": instructions,
            "precondition": precondition,
            "performer": performer,
            "lot_number": lot_number,
            "manufacturer": manufacturer,
            "ids": med_ids,
        })

    return {
        "title": title,
        "code": code,
        "template_ids": template_ids,
        "narrative": narrative,
        "tables": tables,
        "entries": entries,
    }
