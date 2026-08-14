"""
Generic Section Parser for any C-CDA section (Plan of Care, Hospital Course, Chief Complaint, etc.).
Extracts narrative text, structured tables, and any embedded clinical entries.
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


def parse_generic_section(section_el: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Parses any C-CDA section into a rich structured representation with narrative text,
    extracted tables, and generic entry extraction.
    """
    title = get_text(find_child(section_el, "title")) or "Clinical Section"
    text_el = find_child(section_el, "text")
    narrative = extract_narrative_text(text_el)
    tables = parse_narrative_tables(text_el)
    code = parse_code(find_child(section_el, "code"))
    template_ids = get_template_ids(section_el)

    entries: List[Dict[str, Any]] = []

    for entry_el in find_children(section_el, "entry"):
        for child in entry_el:
            parsed_entry = parse_generic_entry(child, ref_map)
            if parsed_entry:
                entries.append(parsed_entry)

    return {
        "title": title,
        "code": code,
        "template_ids": template_ids,
        "narrative": narrative,
        "tables": tables,
        "entries": entries,
    }


def parse_generic_entry(elem: ET.Element, ref_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Generically parse a clinical statement entry (act, observation, procedure, etc.)."""
    tag = elem.tag
    entry_ids = get_ids(elem)
    entry_code = parse_code(find_child(elem, "code"))
    entry_value = parse_value_element(find_child(elem, "value"))
    entry_time = parse_effective_time(find_child(elem, "effectiveTime"))
    status_code = get_attr(find_child(elem, "statusCode"), "code")
    tids = get_template_ids(elem)

    text_el = find_child(elem, "text")
    entry_text = get_text(text_el) if text_el is not None else None
    if text_el is not None:
        ref_el = find_child(text_el, "reference")
        if ref_el is not None and ref_map:
            ref_val = get_attr(ref_el, "value", "").lstrip("#")
            if ref_val in ref_map:
                entry_text = ref_map[ref_val]

    # Nested entry relationships
    relationships: List[Dict[str, Any]] = []
    for rel in find_children(elem, "entryRelationship"):
        type_code = get_attr(rel, "typeCode")
        for rel_child in rel:
            rel_entry = parse_generic_entry(rel_child, ref_map)
            if rel_entry:
                rel_entry["relationship_type"] = type_code
                relationships.append(rel_entry)

    return {
        "statement_type": tag,
        "template_ids": tids,
        "code": entry_code,
        "value": entry_value,
        "text": entry_text,
        "date": entry_time,
        "status": status_code,
        "relationships": relationships if relationships else None,
        "ids": entry_ids,
    }
