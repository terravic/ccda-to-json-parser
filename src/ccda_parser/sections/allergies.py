"""
Allergies and Adverse Reactions Section Parser.
TemplateIds: 2.16.840.1.113883.10.20.22.2.6, 2.16.840.1.113883.10.20.22.2.6.1
LOINC: 48765-2
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


def parse_allergies_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Parse C-CDA Allergies & Intolerances Section."""
    title = get_text(find_child(section_el, "title")) or "Allergies and Adverse Reactions"
    text_el = find_child(section_el, "text")
    narrative = extract_narrative_text(text_el)
    tables = parse_narrative_tables(text_el)
    code = parse_code(find_child(section_el, "code"))
    template_ids = get_template_ids(section_el)

    entries: List[Dict[str, Any]] = []

    # Look for Allergy Concern Acts or direct Allergy Observations
    for entry_el in find_children(section_el, "entry"):
        # Act or Observation
        act_el = find_child(entry_el, "act")
        obs_elements = []

        status_code = None
        concern_effective_time = None
        act_ids = []

        if act_el is not None:
            act_ids = get_ids(act_el)
            status_code = get_attr(find_child(act_el, "statusCode"), "code")
            concern_effective_time = parse_effective_time(find_child(act_el, "effectiveTime"))
            # Find observations inside entryRelationship
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
            obs_type = parse_code(find_child(obs, "code"))  # e.g., Allergy to substance
            obs_value = parse_value_element(find_child(obs, "value"))  # e.g. Propensity to adverse reaction
            obs_time = parse_effective_time(find_child(obs, "effectiveTime"))
            obs_status = get_attr(find_child(obs, "statusCode"), "code")

            # Extract Allergen / Substance
            substance = None
            for part in find_children(obs, "participant"):
                part_role = find_child(part, "participantRole")
                if part_role is not None:
                    playing_entity = find_child(part_role, "playingEntity")
                    if playing_entity is not None:
                        substance = parse_code(find_child(playing_entity, "code"))
                        if not substance:
                            sub_name = get_text(find_child(playing_entity, "name"))
                            if sub_name:
                                substance = {"display_name": sub_name}

            # If substance missing from participant, check value
            if not substance and isinstance(obs_value, dict) and obs_value.get("display_name"):
                substance = obs_value

            # Resolve reference text if name is still missing
            if substance and not substance.get("display_name") and substance.get("reference_id") and ref_map:
                substance["display_name"] = ref_map.get(substance["reference_id"])

            # Reactions / Manifestations and Severity
            reactions: List[Dict[str, Any]] = []
            severity = None
            clinical_status = status_code or obs_status

            for rel in find_children(obs, "entryRelationship"):
                rel_obs = find_child(rel, "observation")
                if rel_obs is None:
                    continue

                rel_tids = get_template_ids(rel_obs)
                rel_code = parse_code(find_child(rel_obs, "code"))
                code_val = rel_code.get("code") if rel_code else ""

                # Reaction observation (2.16.840.1.113883.10.20.22.4.9)
                if any("2.16.840.1.113883.10.20.22.4.9" in t for t in rel_tids) or code_val in ("DX", "ASSERTION", "282191000"):
                    reaction_val = parse_value_element(find_child(rel_obs, "value"))
                    reaction_time = parse_effective_time(find_child(rel_obs, "effectiveTime"))
                    
                    # Reaction severity inside reaction observation
                    rx_severity = None
                    for rx_rel in find_children(rel_obs, "entryRelationship"):
                        rx_sev_obs = find_child(rx_rel, "observation")
                        if rx_sev_obs is not None:
                            sev_val = parse_value_element(find_child(rx_sev_obs, "value"))
                            if sev_val:
                                rx_severity = sev_val

                    reactions.append({
                        "reaction": reaction_val,
                        "time": reaction_time,
                        "severity": rx_severity,
                    })

                # Direct Severity observation (2.16.840.1.113883.10.20.22.4.8) or SEV code
                elif any("2.16.840.1.113883.10.20.22.4.8" in t for t in rel_tids) or code_val in ("SEV", "severity"):
                    sev_val = parse_value_element(find_child(rel_obs, "value"))
                    if sev_val:
                        severity = sev_val

                # Clinical status observation (33999-4)
                elif code_val == "33999-4":
                    stat_val = parse_value_element(find_child(rel_obs, "value"))
                    if isinstance(stat_val, dict) and stat_val.get("display_name"):
                        clinical_status = stat_val.get("display_name")
                    elif isinstance(stat_val, dict) and stat_val.get("code"):
                        clinical_status = stat_val.get("code")

            entries.append({
                "substance": substance,
                "allergy_type": obs_type,
                "status": clinical_status,
                "effective_time": obs_time or concern_effective_time,
                "severity": severity,
                "reactions": reactions,
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
