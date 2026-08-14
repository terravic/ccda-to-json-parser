"""
Encounters Section Parser.
TemplateIds: 2.16.840.1.113883.10.20.22.2.22, 2.16.840.1.113883.10.20.22.2.22.1
LOINC: 46240-8
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


def parse_encounters_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Parse C-CDA Encounters Section."""
    title = get_text(find_child(section_el, "title")) or "Encounters"
    text_el = find_child(section_el, "text")
    narrative = extract_narrative_text(text_el)
    tables = parse_narrative_tables(text_el)
    code = parse_code(find_child(section_el, "code"))
    template_ids = get_template_ids(section_el)

    entries: List[Dict[str, Any]] = []

    for entry_el in find_children(section_el, "entry"):
        enc_el = find_child(entry_el, "encounter")
        if enc_el is None:
            continue

        enc_ids = get_ids(enc_el)
        enc_code = parse_code(find_child(enc_el, "code"))
        enc_time = parse_effective_time(find_child(enc_el, "effectiveTime"))

        if enc_code and not enc_code.get("display_name") and enc_code.get("reference_id") and ref_map:
            enc_code["display_name"] = ref_map.get(enc_code["reference_id"])

        # Performer
        performers: List[Dict[str, Any]] = []
        for perf in find_children(enc_el, "performer"):
            assign_el = find_child(perf, "assignedEntity")
            if assign_el is not None:
                person = find_child(assign_el, "assignedPerson")
                p_code = parse_code(find_child(assign_el, "code"))
                p_name = get_text(find_child(person, "name")) if person is not None else None
                performers.append({
                    "name": p_name,
                    "role": p_code,
                })

        # Location / Facility
        locations: List[Dict[str, Any]] = []
        for part in find_children(enc_el, "participant"):
            part_role = find_child(part, "participantRole")
            if part_role is not None:
                play_entity = find_child(part_role, "playingEntity")
                loc_name = get_text(find_child(play_entity, "name")) if play_entity is not None else None
                loc_code = parse_code(find_child(part_role, "code"))
                if loc_name or loc_code:
                    locations.append({
                        "name": loc_name,
                        "type": loc_code,
                    })

        # Diagnoses / Indications in entryRelationship
        diagnoses: List[Dict[str, Any]] = []
        for rel in find_children(enc_el, "entryRelationship"):
            obs = find_child(rel, "observation")
            act = find_child(rel, "act")
            target = obs if obs is not None else act
            if target is not None:
                val = parse_value_element(find_child(target, "value"))
                t_code = parse_code(find_child(target, "code"))
                diagnoses.append({
                    "code": t_code,
                    "value": val,
                })

        entries.append({
            "encounter_type": enc_code,
            "date": enc_time,
            "performers": performers,
            "locations": locations,
            "diagnoses": diagnoses,
            "ids": enc_ids,
        })

    return {
        "title": title,
        "code": code,
        "template_ids": template_ids,
        "narrative": narrative,
        "tables": tables,
        "entries": entries,
    }
