"""
Date and timestamp parsing utilities for HL7 C-CDA datetime formats.

Handles:
- HL7 TS (Time Stamp): YYYY, YYYYMM, YYYYMMDD, YYYYMMDDHHMMSS, with/without timezone offsets
- IVL_TS (Interval Time Stamp): low, high, center, width
- PIVL_TS (Periodic Interval): period, unit, phase
- nullFlavor values (UNK, NA, NI, etc.)
"""

import re
from typing import Any, Dict, Optional, Union
import xml.etree.ElementTree as ET

from .xml_utils import find_child, get_attr, get_null_flavor


def parse_hl7_date(ts_str: Optional[str]) -> Optional[str]:
    """
    Converts an HL7 timestamp string into an ISO-8601 formatted date/datetime string.

    Examples:
        "20230514" -> "2023-05-14"
        "202305141530" -> "2023-05-14T15:30:00"
        "20230514153022" -> "2023-05-14T15:30:22"
        "20230514153022-0400" -> "2023-05-14T15:30:22-04:00"
        "20230514153022+0000" -> "2023-05-14T15:30:22Z"
        "2023" -> "2023"
        "202305" -> "2023-05"
    """
    if not ts_str or not isinstance(ts_str, str):
        return None

    s = ts_str.strip()
    if not s:
        return None

    # Handle timezone offset if present
    tz_part = ""
    if "+" in s:
        s, tz_raw = s.split("+", 1)
        if tz_raw == "0000" or tz_raw == "00":
            tz_part = "Z"
        elif len(tz_raw) == 4:
            tz_part = f"+{tz_raw[:2]}:{tz_raw[2:]}"
        else:
            tz_part = f"+{tz_raw}"
    elif "-" in s and len(s) > 8 and not re.match(r"^\d{4}-\d{2}-\d{2}", s):
        # Only split if it's an HL7 offset (e.g. 20230514153022-0400), not already ISO
        parts = s.split("-")
        if len(parts) == 2 and len(parts[0]) >= 8:
            s, tz_raw = parts[0], parts[1]
            if len(tz_raw) == 4:
                tz_part = f"-{tz_raw[:2]}:{tz_raw[2:]}"
            else:
                tz_part = f"-{tz_raw}"

    # Extract digits and optional milliseconds
    match = re.match(r"^(\d+)(?:\.(\d+))?", s)
    if not match:
        # Fallback if already ISO formatted or contains other string
        return ts_str

    digits = match.group(1)
    millis = match.group(2)
    ms_str = f".{millis[:3]}" if millis else ""

    length = len(digits)
    if length >= 14:
        # YYYYMMDDHHMMSS
        year = digits[0:4]
        month = digits[4:6]
        day = digits[6:8]
        hour = digits[8:10]
        minute = digits[10:12]
        sec = digits[12:14]
        return f"{year}-{month}-{day}T{hour}:{minute}:{sec}{ms_str}{tz_part}"
    elif length == 12:
        # YYYYMMDDHHMM
        year = digits[0:4]
        month = digits[4:6]
        day = digits[6:8]
        hour = digits[8:10]
        minute = digits[10:12]
        return f"{year}-{month}-{day}T{hour}:{minute}:00{tz_part}"
    elif length == 10:
        # YYYYMMDDHH
        year = digits[0:4]
        month = digits[4:6]
        day = digits[6:8]
        hour = digits[8:10]
        return f"{year}-{month}-{day}T{hour}:00:00{tz_part}"
    elif length == 8:
        # YYYYMMDD
        year = digits[0:4]
        month = digits[4:6]
        day = digits[6:8]
        return f"{year}-{month}-{day}"
    elif length == 6:
        # YYYYMM
        year = digits[0:4]
        month = digits[4:6]
        return f"{year}-{month}"
    elif length == 4:
        # YYYY
        return digits[0:4]

    return ts_str


def parse_effective_time(elem: Optional[ET.Element]) -> Optional[Union[str, Dict[str, Any]]]:
    """
    Parses an effectiveTime or time element.
    Returns:
        - ISO date string if single time point (e.g. value="20230514")
        - Dictionary with low, high, center, period, etc. for intervals
        - None if empty or nullFlavor
    """
    if elem is None:
        return None

    null_flavor = get_null_flavor(elem)
    if null_flavor:
        return {"null_flavor": null_flavor}

    # Case 1: Direct value attribute (e.g., <effectiveTime value="20230514120000"/>)
    val = get_attr(elem, "value")
    if val:
        parsed_val = parse_hl7_date(val)
        return parsed_val

    result: Dict[str, Any] = {}

    # Case 2: Interval with <low> and/or <high>
    low_el = find_child(elem, "low")
    if low_el is not None:
        low_nf = get_null_flavor(low_el)
        if low_nf:
            result["low"] = {"null_flavor": low_nf}
        else:
            low_val = get_attr(low_el, "value")
            result["low"] = parse_hl7_date(low_val) if low_val else None

    high_el = find_child(elem, "high")
    if high_el is not None:
        high_nf = get_null_flavor(high_el)
        if high_nf:
            result["high"] = {"null_flavor": high_nf}
        else:
            high_val = get_attr(high_el, "value")
            result["high"] = parse_hl7_date(high_val) if high_val else None

    center_el = find_child(elem, "center")
    if center_el is not None:
        center_val = get_attr(center_el, "value")
        result["center"] = parse_hl7_date(center_val) if center_val else None

    width_el = find_child(elem, "width")
    if width_el is not None:
        result["width"] = {
            "value": get_attr(width_el, "value"),
            "unit": get_attr(width_el, "unit"),
        }

    # Case 3: Periodic interval <period value="8" unit="h"/>
    period_el = find_child(elem, "period")
    if period_el is not None:
        p_val = get_attr(period_el, "value")
        p_unit = get_attr(period_el, "unit")
        result["period"] = {
            "value": p_val,
            "unit": p_unit,
            "human_readable": format_period(p_val, p_unit) if p_val and p_unit else None,
        }

    if not result:
        return None

    # If only low is present and high is absent, or vice versa, return clean dict
    return result


def format_period(value: str, unit: str) -> str:
    """Format HL7 period unit into human-readable frequency."""
    unit_map = {
        "h": "hours",
        "d": "days",
        "wk": "weeks",
        "mo": "months",
        "min": "minutes",
        "s": "seconds",
    }
    unit_name = unit_map.get(unit.lower(), unit)
    if value == "1":
        unit_name = unit_name.rstrip("s")
        return f"Every {unit_name}"
    elif value == "24" and unit.lower() == "h":
        return "Daily"
    elif value == "12" and unit.lower() == "h":
        return "Twice daily (q12h)"
    elif value == "8" and unit.lower() == "h":
        return "Three times daily (q8h)"
    elif value == "6" and unit.lower() == "h":
        return "Four times daily (q6h)"
    elif value == "4" and unit.lower() == "h":
        return "Every 4 hours (q4h)"
    return f"Every {value} {unit_name}"
