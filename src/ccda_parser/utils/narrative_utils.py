"""
Narrative text parsing, HTML table structure extraction, and reference resolution for C-CDA sections.
"""

import re
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

from .xml_utils import find_all_descendants, find_children, get_attr, get_text


def extract_narrative_text(text_el: Optional[ET.Element]) -> str:
    """
    Extracts clean, readable narrative text from a section's <text> element,
    preserving paragraph and table structure in human-friendly text format.
    """
    if text_el is None:
        return ""

    lines: List[str] = []
    
    # Process children
    for child in text_el:
        tag = child.tag.lower()
        if tag in ("paragraph", "p"):
            p_text = get_text(child)
            if p_text:
                lines.append(p_text)
        elif tag in ("list",):
            for item in find_children(child, "item"):
                item_text = get_text(item)
                if item_text:
                    lines.append(f"• {item_text}")
        elif tag in ("table",):
            table_str = table_to_string(child)
            if table_str:
                lines.append(table_str)
        else:
            t = get_text(child)
            if t:
                lines.append(t)

    # If no child elements produced output, get plain inner text
    if not lines:
        raw = get_text(text_el)
        # Normalize whitespace
        raw = re.sub(r"\s+", " ", raw).strip()
        return raw

    return "\n".join(lines).strip()


def table_to_string(table_el: ET.Element) -> str:
    """Converts a C-CDA XML table element into a formatted text string."""
    headers: List[str] = []
    thead = None
    for child in table_el:
        if child.tag.lower() == "thead":
            thead = child
            break

    if thead is not None:
        for tr in find_all_descendants(thead, "tr"):
            for th in list(tr):
                headers.append(get_text(th))

    rows: List[List[str]] = []
    for tr in find_all_descendants(table_el, "tr"):
        if thead is not None and tr in list(thead):
            continue
        cells = [get_text(td) for td in list(tr) if td.tag.lower() in ("td", "th")]
        if cells and any(cells):
            rows.append(cells)

    lines: List[str] = []
    if headers:
        lines.append(" | ".join(headers))
        lines.append("-" * len(" | ".join(headers)))
    for row in rows:
        lines.append(" | ".join(row))

    return "\n".join(lines)


def parse_narrative_tables(text_el: Optional[ET.Element]) -> List[Dict[str, Any]]:
    """
    Parses any <table> elements inside a <text> element into structured JSON objects.
    Returns a list of table definitions with columns and rows (as dicts if headers exist).
    """
    if text_el is None:
        return []

    tables: List[Dict[str, Any]] = []
    for table_el in find_all_descendants(text_el, "table"):
        headers: List[str] = []
        for th in find_all_descendants(table_el, "th"):
            h_text = get_text(th)
            if h_text:
                headers.append(h_text)

        # Fallback: if no <th>, check first <tr>
        rows_raw: List[List[str]] = []
        for tr in find_all_descendants(table_el, "tr"):
            cells = [get_text(td) for td in list(tr) if td.tag.lower() in ("td", "th")]
            if cells and any(cells):
                rows_raw.append(cells)

        if not headers and rows_raw:
            # First row might be header
            headers = rows_raw[0]
            data_rows = rows_raw[1:]
        else:
            data_rows = [r for r in rows_raw if r != headers]

        # Convert to list of dicts if headers match row lengths
        structured_rows: List[Any] = []
        for row in data_rows:
            if headers and len(headers) == len(row):
                structured_rows.append(dict(zip(headers, row)))
            else:
                structured_rows.append(row)

        caption = None
        for cap in find_children(table_el, "caption"):
            caption = get_text(cap)

        tables.append({
            "caption": caption,
            "headers": headers,
            "rows": structured_rows,
        })

    return tables


def build_id_reference_map(root: ET.Element) -> Dict[str, str]:
    """
    Builds a dictionary mapping all elements with ID or id attributes
    to their clean text content (useful for resolving <reference value="#xxx"/>).
    """
    ref_map: Dict[str, str] = {}
    for el in root.iter():
        elem_id = get_attr(el, "ID") or get_attr(el, "id")
        if elem_id and isinstance(elem_id, str):
            text = get_text(el)
            if text:
                ref_map[elem_id] = text
    return ref_map
