"""
Data models and JSON schema definitions for C-CDA Parsed Clinical Data.
"""

from dataclasses import asdict, dataclass, field
import json
from typing import Any, Dict, List, Optional


@dataclass
class CodedConcept:
    code: Optional[str] = None
    display_name: Optional[str] = None
    code_system: Optional[str] = None
    code_system_name: Optional[str] = None
    code_system_version: Optional[str] = None
    original_text: Optional[str] = None
    translations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PatientDemographics:
    name: Optional[Dict[str, Any]] = None
    gender: Optional[Dict[str, Any]] = None
    birth_time: Optional[str] = None
    marital_status: Optional[Dict[str, Any]] = None
    race: Optional[Dict[str, Any]] = None
    ethnicity: Optional[Dict[str, Any]] = None
    ids: List[Dict[str, str]] = field(default_factory=list)
    addresses: List[Dict[str, Any]] = field(default_factory=list)
    telecoms: List[Dict[str, Any]] = field(default_factory=list)
    languages: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ParsedCCDA:
    """Root representation of a parsed C-CDA Document in JSON format."""
    document_meta: Dict[str, Any] = field(default_factory=dict)
    patient: Dict[str, Any] = field(default_factory=dict)
    sections: Dict[str, Any] = field(default_factory=dict)
    all_sections: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to standard Python dictionary."""
        return {
            "document_meta": self.document_meta,
            "patient": self.patient,
            "sections": self.sections,
            "all_sections": self.all_sections,
        }

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, default=str)
