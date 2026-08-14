"""
Social History Section Parser.
TemplateIds: 2.16.840.1.113883.10.20.22.2.17
LOINC: 29762-2
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


def parse_social_history_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Parse C-CDA Social History Section."""
    title = get_text(find_child(section_el, "title")) or "Social History"
    text_el = find_child(section_el, "text")
    narrative = extract_narrative_text(text_el)
    tables = parse_narrative_tables(text_el)
    code = parse_code(find_child(section_el, "code"))
    template_ids = get_template_ids(section_el)

    smoking_status = None
    entries: List[Dict[str, Any]] = []

    for entry_el in find_children(section_el, "entry"):
        obs = find_child(entry_el, "observation")
        if obs is None:
            continue

        obs_ids = get_ids(obs)
        obs_code = parse_code(find_child(obs, "code"))
        obs_val = parse_value_element(find_child(obs, "value"))
        obs_time = parse_effective_time(find_child(obs, "effectiveTime"))
        obs_status = get_attr(find_child(obs, "statusCode"), "code")
        obs_tids = get_template_ids(obs)

        code_val = obs_code.get("code") if obs_code else ""

        # Check for Smoking Status Observation (72166-2 or template 2.16.840.1.113883.10.20.22.4.78)
        if code_val in ("72166-2", "ASSERTION") or any("2.16.840.1.113883.10.20.22.4.78" in t for t in obs_tids):
            smoking_status = {
                "status": obs_val,
                "date": obs_time,
                "ids": obs_ids,
            }

        entries.append({
            "observation": obs_code,
            "value": obs_val,
            "date": obs_time,
            "status": obs_status,
            "ids": obs_ids,
        })

    return {
        "title": title,
        "code": code,
        "template_ids": template_ids,
        "narrative": narrative,
        "tables": tables,
        "smoking_status": smoking_status,
        "entries": entries,
    }
