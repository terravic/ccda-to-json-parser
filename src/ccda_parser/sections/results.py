"""
Diagnostic Results / Laboratory Tests Section Parser.
TemplateIds: 2.16.840.1.113883.10.20.22.2.3, 2.16.840.1.113883.10.20.22.2.3.1
LOINC: 30954-2
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


def parse_results_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Parse C-CDA Diagnostic Results Section."""
    title = get_text(find_child(section_el, "title")) or "Diagnostic Results"
    text_el = find_child(section_el, "text")
    narrative = extract_narrative_text(text_el)
    tables = parse_narrative_tables(text_el)
    code = parse_code(find_child(section_el, "code"))
    template_ids = get_template_ids(section_el)

    panels: List[Dict[str, Any]] = []
    flat_results: List[Dict[str, Any]] = []

    for entry_el in find_children(section_el, "entry"):
        organizer_el = find_child(entry_el, "organizer")

        if organizer_el is not None:
            org_ids = get_ids(organizer_el)
            org_code = parse_code(find_child(organizer_el, "code"))
            org_status = get_attr(find_child(organizer_el, "statusCode"), "code")
            org_time = parse_effective_time(find_child(organizer_el, "effectiveTime"))

            lab_results: List[Dict[str, Any]] = []
            for comp in find_children(organizer_el, "component"):
                obs = find_child(comp, "observation")
                if obs is not None:
                    res = parse_result_observation(obs, org_time, ref_map)
                    lab_results.append(res)
                    flat_results.append(res)

            panels.append({
                "panel_name": org_code.get("display_name") if org_code else "Laboratory Panel",
                "panel_code": org_code,
                "date": org_time,
                "status": org_status,
                "results": lab_results,
                "ids": org_ids,
            })
        else:
            obs = find_child(entry_el, "observation")
            if obs is not None:
                res = parse_result_observation(obs, None, ref_map)
                flat_results.append(res)

    return {
        "title": title,
        "code": code,
        "template_ids": template_ids,
        "narrative": narrative,
        "tables": tables,
        "panels": panels,
        "results": flat_results,
    }


def parse_result_observation(obs: ET.Element, default_time: Optional[Any] = None, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Parse single Result observation element."""
    obs_ids = get_ids(obs)
    obs_code = parse_code(find_child(obs, "code"))
    obs_val = parse_value_element(find_child(obs, "value"))
    obs_time = parse_effective_time(find_child(obs, "effectiveTime")) or default_time
    obs_status = get_attr(find_child(obs, "statusCode"), "code")

    # Interpretation
    interp_el = find_child(obs, "interpretationCode")
    interpretation = parse_code(interp_el)

    # Reference range
    reference_range = None
    ref_el = find_child(obs, "referenceRange")
    if ref_el is not None:
        obs_range = find_child(ref_el, "observationRange")
        if obs_range is not None:
            reference_range = parse_value_element(find_child(obs_range, "value")) or get_text(find_child(obs_range, "text"))

    if obs_code and not obs_code.get("display_name") and obs_code.get("reference_id") and ref_map:
        obs_code["display_name"] = ref_map.get(obs_code["reference_id"])

    return {
        "test": obs_code,
        "value": obs_val,
        "interpretation": interpretation,
        "reference_range": reference_range,
        "date": obs_time,
        "status": obs_status,
        "ids": obs_ids,
    }
