"""
Procedures Section Parser.
TemplateIds: 2.16.840.1.113883.10.20.22.2.7, 2.16.840.1.113883.10.20.22.2.7.1
LOINC: 47519-4
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


def parse_procedures_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Parse C-CDA Procedures Section."""
    title = get_text(find_child(section_el, "title")) or "Procedures"
    text_el = find_child(section_el, "text")
    narrative = extract_narrative_text(text_el)
    tables = parse_narrative_tables(text_el)
    code = parse_code(find_child(section_el, "code"))
    template_ids = get_template_ids(section_el)

    entries: List[Dict[str, Any]] = []

    for entry_el in find_children(section_el, "entry"):
        # Can be procedure, observation, or act
        proc_el = find_child(entry_el, "procedure")
        if proc_el is None:
            proc_el = find_child(entry_el, "observation")
        if proc_el is None:
            proc_el = find_child(entry_el, "act")
        if proc_el is None:
            continue

        proc_ids = get_ids(proc_el)
        proc_code = parse_code(find_child(proc_el, "code"))
        proc_time = parse_effective_time(find_child(proc_el, "effectiveTime"))
        proc_status = get_attr(find_child(proc_el, "statusCode"), "code")
        target_site = parse_code(find_child(proc_el, "targetSiteCode"))

        if proc_code and not proc_code.get("display_name") and proc_code.get("reference_id") and ref_map:
            proc_code["display_name"] = ref_map.get(proc_code["reference_id"])

        # Performer
        performers: List[Dict[str, Any]] = []
        for perf in find_children(proc_el, "performer"):
            assign_el = find_child(perf, "assignedEntity")
            if assign_el is not None:
                person = find_child(assign_el, "assignedPerson")
                p_name = get_text(find_child(person, "name")) if person is not None else None
                p_role = parse_code(find_child(assign_el, "code"))
                performers.append({
                    "name": p_name,
                    "role": p_role,
                })

        # Devices / Implants
        devices: List[Dict[str, Any]] = []
        for part in find_children(proc_el, "participant"):
            part_role = find_child(part, "participantRole")
            if part_role is not None:
                device = find_child(part_role, "playingDevice")
                if device is not None:
                    dev_code = parse_code(find_child(device, "code"))
                    devices.append(dev_code)

        entries.append({
            "procedure": proc_code,
            "status": proc_status,
            "date": proc_time,
            "target_site": target_site,
            "performers": performers,
            "devices": devices if devices else None,
            "ids": proc_ids,
        })

    return {
        "title": title,
        "code": code,
        "template_ids": template_ids,
        "narrative": narrative,
        "tables": tables,
        "entries": entries,
    }
