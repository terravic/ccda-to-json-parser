"""
Problems / Conditions / Health Concerns Section Parser.
TemplateIds: 2.16.840.1.113883.10.20.22.2.5, 2.16.840.1.113883.10.20.22.2.5.1
LOINC: 11450-4, 18776-5
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


def parse_problems_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Parse C-CDA Problems Section."""
    title = get_text(find_child(section_el, "title")) or "Problems and Conditions"
    text_el = find_child(section_el, "text")
    narrative = extract_narrative_text(text_el)
    tables = parse_narrative_tables(text_el)
    code = parse_code(find_child(section_el, "code"))
    template_ids = get_template_ids(section_el)

    entries: List[Dict[str, Any]] = []

    for entry_el in find_children(section_el, "entry"):
        act_el = find_child(entry_el, "act")
        obs_elements = []

        concern_status = None
        concern_time = None
        act_ids = []

        if act_el is not None:
            act_ids = get_ids(act_el)
            concern_status = get_attr(find_child(act_el, "statusCode"), "code")
            concern_time = parse_effective_time(find_child(act_el, "effectiveTime"))
            for rel in find_children(act_el, "entryRelationship"):
                obs = find_child(rel, "observation")
                if obs is not None:
                    obs_elements.append(obs)
        else:
            obs = find_child(entry_el, "observation")
            if obs is not None:
                obs_elements.append(obs)

        for obs in obs_elements:
            obs_ids = get_ids(obs)
            obs_type = parse_code(find_child(obs, "code"))
            obs_value = parse_value_element(find_child(obs, "value"))
            obs_time = parse_effective_time(find_child(obs, "effectiveTime"))
            obs_status = get_attr(find_child(obs, "statusCode"), "code")

            # Problem value / condition name
            problem = obs_value if isinstance(obs_value, dict) else {"display_name": str(obs_value) if obs_value else None}

            # Resolve originalText / reference from ref_map
            if problem and not problem.get("display_name") and problem.get("reference_id") and ref_map:
                problem["display_name"] = ref_map.get(problem["reference_id"])

            clinical_status = concern_status or obs_status
            age_at_onset = None
            health_status = None

            for rel in find_children(obs, "entryRelationship"):
                rel_obs = find_child(rel, "observation")
                if rel_obs is None:
                    continue

                rel_tids = get_template_ids(rel_obs)
                rel_code = parse_code(find_child(rel_obs, "code"))
                code_val = rel_code.get("code") if rel_code else ""

                # Problem Status Observation (33999-4 or 2.16.840.1.113883.10.20.22.4.6)
                if code_val == "33999-4" or any("2.16.840.1.113883.10.20.22.4.6" in t for t in rel_tids):
                    status_val = parse_value_element(find_child(rel_obs, "value"))
                    if isinstance(status_val, dict) and status_val.get("display_name"):
                        clinical_status = status_val.get("display_name")
                    elif isinstance(status_val, dict) and status_val.get("code"):
                        clinical_status = status_val.get("code")

                # Age Observation (2.16.840.1.113883.10.20.22.4.31)
                elif any("2.16.840.1.113883.10.20.22.4.31" in t for t in rel_tids) or code_val == "445518008":
                    age_at_onset = parse_value_element(find_child(rel_obs, "value"))

                # Health Status Observation (11323-3)
                elif code_val == "11323-3":
                    health_status = parse_value_element(find_child(rel_obs, "value"))

            entries.append({
                "problem": problem,
                "problem_type": obs_type,
                "status": clinical_status,
                "effective_time": obs_time or concern_time,
                "age_at_onset": age_at_onset,
                "health_status": health_status,
                "ids": obs_ids or act_ids,
            })

    return {
        "title": title,
        "code": code,
        "template_ids": template_ids,
        "narrative": narrative,
        "tables": tables,
        "entries": entries,
    }
