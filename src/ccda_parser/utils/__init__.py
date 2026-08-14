"""Utility modules for C-CDA parsing."""

from .xml_utils import (
    find_child,
    find_children,
    find_descendant,
    find_all_descendants,
    get_attr,
    get_null_flavor,
    get_text,
    get_template_ids,
    get_ids,
    parse_xml,
    strip_namespaces,
)
from .date_utils import parse_hl7_date, parse_effective_time, format_period
from .code_utils import parse_code, parse_single_code, parse_value_element, KNOWN_CODE_SYSTEMS
from .narrative_utils import (
    extract_narrative_text,
    parse_narrative_tables,
    build_id_reference_map,
)

__all__ = [
    "find_child",
    "find_children",
    "find_descendant",
    "find_all_descendants",
    "get_attr",
    "get_null_flavor",
    "get_text",
    "get_template_ids",
    "get_ids",
    "parse_xml",
    "strip_namespaces",
    "parse_hl7_date",
    "parse_effective_time",
    "format_period",
    "parse_code",
    "parse_single_code",
    "parse_value_element",
    "KNOWN_CODE_SYSTEMS",
    "extract_narrative_text",
    "parse_narrative_tables",
    "build_id_reference_map",
]
