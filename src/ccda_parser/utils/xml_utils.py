"""
XML parsing and traversal utilities for C-CDA documents.

Handles namespace stripping, prefix management, robust element lookup,
and nullFlavor / attribute extraction.
"""

from typing import Dict, List, Optional, Union
import xml.etree.ElementTree as ET


def strip_namespaces(elem: ET.Element) -> ET.Element:
    """
    Recursively remove XML namespaces from an ElementTree element and its children.
    This simplifies element querying when dealing with mixed or prefixed C-CDA namespaces
    (e.g., urn:hl7-org:v3, sdtc, xsi).
    """
    for el in elem.iter():
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]  # Strip namespace URI
        # Clean attributes
        attrib_keys = list(el.attrib.keys())
        for key in attrib_keys:
            if "}" in key:
                clean_key = key.split("}", 1)[1]
                el.attrib[clean_key] = el.attrib.pop(key)
    return elem


def parse_xml(xml_source: Union[str, bytes], strip_ns: bool = True) -> ET.Element:
    """
    Parses an XML string or file path into an ElementTree Element.
    
    Args:
        xml_source: XML string content or file path or raw bytes.
        strip_ns: Whether to strip namespaces for easier processing.
        
    Returns:
        Root ET.Element of the XML document.
    """
    if isinstance(xml_source, str) and not xml_source.strip().startswith("<"):
        # It is a file path
        tree = ET.parse(xml_source)
        root = tree.getroot()
    elif isinstance(xml_source, (str, bytes)):
        # XML string or bytes content
        root = ET.fromstring(xml_source)
    elif isinstance(xml_source, ET.Element):
        root = xml_source
    else:
        raise ValueError(f"Unsupported XML source type: {type(xml_source)}")
        
    if strip_ns:
        strip_namespaces(root)
        
    return root


def find_child(elem: Optional[ET.Element], tag: str) -> Optional[ET.Element]:
    """Find direct child element by local tag name."""
    if elem is None:
        return None
    for child in elem:
        if child.tag == tag:
            return child
    return None


def find_children(elem: Optional[ET.Element], tag: str) -> List[ET.Element]:
    """Find all direct child elements matching local tag name."""
    if elem is None:
        return []
    return [child for child in elem if child.tag == tag]


def find_descendant(elem: Optional[ET.Element], path: str) -> Optional[ET.Element]:
    """
    Find first descendant matching a '/'-separated tag path.
    Example: find_descendant(root, "recordTarget/patientRole/patient")
    """
    if elem is None:
        return None
    parts = path.split("/")
    curr = elem
    for part in parts:
        curr = find_child(curr, part)
        if curr is None:
            return None
    return curr


def find_all_descendants(elem: Optional[ET.Element], tag: str) -> List[ET.Element]:
    """Find all descendants with the matching local tag name anywhere in subtree."""
    if elem is None:
        return []
    return list(elem.iter(tag))


def get_attr(elem: Optional[ET.Element], attr_name: str, default: Optional[str] = None) -> Optional[str]:
    """Safely get attribute value from element."""
    if elem is None or not elem.attrib:
        return default
    return elem.attrib.get(attr_name, default)


def get_null_flavor(elem: Optional[ET.Element]) -> Optional[str]:
    """Return nullFlavor attribute value if present."""
    if elem is None:
        return None
    return elem.attrib.get("nullFlavor")


def get_text(elem: Optional[ET.Element], default: str = "") -> str:
    """Safely extract stripped inner text of an element."""
    if elem is None:
        return default
    return "".join(elem.itertext()).strip() or default


def get_template_ids(elem: Optional[ET.Element]) -> List[str]:
    """Extract all templateId root strings from an element."""
    if elem is None:
        return []
    template_ids = []
    for tid in find_children(elem, "templateId"):
        root = get_attr(tid, "root")
        ext = get_attr(tid, "extension")
        if root:
            if ext:
                template_ids.append(f"{root}:{ext}")
            else:
                template_ids.append(root)
    return template_ids


def get_ids(elem: Optional[ET.Element]) -> List[Dict[str, str]]:
    """Extract all id elements with root, extension, and assigningAuthorityName."""
    if elem is None:
        return []
    ids = []
    for id_el in find_children(elem, "id"):
        id_dict = {}
        root = get_attr(id_el, "root")
        ext = get_attr(id_el, "extension")
        auth = get_attr(id_el, "assigningAuthorityName")
        if root:
            id_dict["root"] = root
        if ext:
            id_dict["extension"] = ext
        if auth:
            id_dict["assigningAuthorityName"] = auth
        if id_dict:
            ids.append(id_dict)
    return ids
