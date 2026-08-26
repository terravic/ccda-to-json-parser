#!/usr/bin/env python3
"""
Interactive C-CDA to JSON Mapping Dashboard Generator.
Generates a self-contained, enterprise-grade, interactive Canvas UI dashboard
documenting the complete mapping specification, field explanations, code systems,
and live sample explorer between HL7 C-CDA XML and standardized JSON.
"""

import json
import os
import sys

# Dashboard mapping dataset
MAPPING_SECTIONS = [
    {
        "id": "header_demographics",
        "title": "Document Header & Demographics",
        "badge": "Core Metadata",
        "loinc": "34133-9 / 11488-4",
        "cda_template": "2.16.840.1.113883.10.20.22.1.1 (US Realm Header)",
        "description": "Defines patient identity, demographics, legal authenticators, authors, custodians, document metadata, and confidentiality codes.",
        "xml_snippet": """<ClinicalDocument xmlns="urn:hl7-org:v3" xmlns:sdtc="urn:hl7-org:sdtc">
  <realmCode code="US"/>
  <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
  <templateId root="2.16.840.1.113883.10.20.22.1.1" extension="2015-08-01"/>
  <id root="2.16.840.1.113883.19.5" extension="CCD-2023-009182"/>
  <code code="34133-9" codeSystem="2.16.840.1.113883.6.1" displayName="Summarization of Episode Note"/>
  <title>Continuity of Care Document (CCD)</title>
  <effectiveTime value="20230514143000-0500"/>
  <confidentialityCode code="N" codeSystem="2.16.840.1.113883.5.25" displayName="Normal"/>
  <recordTarget>
    <patientRole>
      <id root="2.16.840.1.113883.19.5" extension="MRN-8849201" assigningAuthorityName="Metropolitan Health"/>
      <addr use="HP">
        <streetAddressLine>742 Evergreen Terrace</streetAddressLine>
        <city>Springfield</city>
        <state>IL</state>
        <postalCode>62704</postalCode>
        <country>US</country>
      </addr>
      <telecom use="HP" value="tel:+1-555-733-4001"/>
      <patient>
        <name use="L">
          <prefix>Ms.</prefix>
          <given>Eleanor</given>
          <given qualifier="IN">Marie</given>
          <family>Vance</family>
        </name>
        <administrativeGenderCode code="F" codeSystem="2.16.840.1.113883.5.1" displayName="Female"/>
        <birthTime value="19750822"/>
        <maritalStatusCode code="M" codeSystem="2.16.840.1.113883.5.2" displayName="Married"/>
        <raceCode code="2106-3" codeSystem="2.16.840.1.113883.6.238" displayName="White"/>
        <ethnicGroupCode code="2186-5" codeSystem="2.16.840.1.113883.6.238" displayName="Not Hispanic or Latino"/>
      </patient>
    </patientRole>
  </recordTarget>
</ClinicalDocument>""",
        "json_snippet": """{
  "document_meta": {
    "document_id": {
      "root": "2.16.840.1.113883.19.5",
      "extension": "CCD-2023-009182"
    },
    "document_type": {
      "code": "34133-9",
      "code_system": "2.16.840.1.113883.6.1",
      "code_system_name": "LOINC",
      "display_name": "Summarization of Episode Note"
    },
    "title": "Continuity of Care Document (CCD)",
    "effective_time": "2023-05-14T14:30:00-05:00",
    "confidentiality": {
      "code": "N",
      "display_name": "Normal"
    },
    "template_ids": ["2.16.840.1.113883.10.20.22.1.1:2015-08-01"]
  },
  "patient": {
    "ids": [{
      "root": "2.16.840.1.113883.19.5",
      "extension": "MRN-8849201",
      "assigningAuthorityName": "Metropolitan Health"
    }],
    "name": {
      "full_name": "Ms. Eleanor Marie Vance",
      "first_name": "Eleanor",
      "middle_names": ["Marie"],
      "last_name": "Vance",
      "prefixes": ["Ms."]
    },
    "gender": {
      "code": "F",
      "display_name": "Female"
    },
    "birth_time": "1975-08-22",
    "marital_status": {"code": "M", "display_name": "Married"},
    "race": {"code": "2106-3", "display_name": "White"},
    "ethnicity": {"code": "2186-5", "display_name": "Not Hispanic or Latino"},
    "addresses": [{
      "street_address_lines": ["742 Evergreen Terrace"],
      "city": "Springfield",
      "state": "IL",
      "postal_code": "62704",
      "country": "US",
      "formatted": "742 Evergreen Terrace, Springfield, IL 62704, US"
    }],
    "telecoms": [{"system": "tel", "value": "+1-555-733-4001", "use": "HP"}]
  }
}""",
        "fields": [
            {
                "xml_path": "ClinicalDocument/id/@root + @extension",
                "json_path": "document_meta.document_id",
                "data_type": "II (Instance Identifier)",
                "code_system": "ISO OID",
                "description": "Globally unique identifier for the clinical document instance. Maps root OID and optional extension string.",
                "rules": "Combines root and extension; preserves assigning authority."
            },
            {
                "xml_path": "ClinicalDocument/code/@code + @displayName",
                "json_path": "document_meta.document_type",
                "data_type": "CD (Concept Descriptor)",
                "code_system": "LOINC (2.16.840.1.113883.6.1)",
                "description": "Specifies clinical document type (CCD, Discharge Summary, Referral Note, Care Plan).",
                "rules": "Resolves LOINC OID to friendly system name 'LOINC'. Fallbacks to internal code lookup if displayName is omitted."
            },
            {
                "xml_path": "ClinicalDocument/effectiveTime/@value",
                "json_path": "document_meta.effective_time",
                "data_type": "TS (Timestamp)",
                "code_system": "ISO-8601",
                "description": "Document creation or signing timestamp.",
                "rules": "Converts HL7 TS format (YYYYMMDDHHMMSS[+/-ZZZZ]) to standardized ISO-8601 format with timezone offset."
            },
            {
                "xml_path": "recordTarget/patientRole/id",
                "json_path": "patient.ids[]",
                "data_type": "II (Instance Identifier)",
                "code_system": "Hospital OID",
                "description": "List of patient identifiers such as Medical Record Number (MRN) and National IDs.",
                "rules": "Extracts all ID elements with their assigning authority."
            },
            {
                "xml_path": "patientRole/patient/name",
                "json_path": "patient.name",
                "data_type": "PN (Person Name)",
                "code_system": "HL7 CDA R2",
                "description": "Patient's legal name, broken down into structured components and combined into full_name.",
                "rules": "Handles multiple given names (distinguishing first vs. middle qualifiers), prefixes (Mr., Ms., Dr.), and suffixes (Jr., III)."
            },
            {
                "xml_path": "patientRole/patient/administrativeGenderCode",
                "json_path": "patient.gender",
                "data_type": "CE (Coded with Equiv)",
                "code_system": "HL7 AdministrativeGender (2.16.840.1.113883.5.1)",
                "description": "Administrative biological gender (M, F, UN).",
                "rules": "Maps standard HL7 gender codes to human-readable display names."
            },
            {
                "xml_path": "patientRole/patient/birthTime/@value",
                "json_path": "patient.birth_time",
                "data_type": "TS (Timestamp / Date)",
                "code_system": "ISO-8601 Date",
                "description": "Patient's legal date of birth.",
                "rules": "Normalized to 'YYYY-MM-DD' calendar date string."
            },
            {
                "xml_path": "patientRole/addr",
                "json_path": "patient.addresses[]",
                "data_type": "AD (Postal Address)",
                "code_system": "US Postal / Standard",
                "description": "Patient postal address lines, city, state, zip, country, and pre-formatted single-line address.",
                "rules": "Aggregates street lines into an array and generates 'formatted' string helper."
            },
            {
                "xml_path": "patientRole/telecom",
                "json_path": "patient.telecoms[]",
                "data_type": "TEL (Telecommunication)",
                "code_system": "RFC 3966 / URI",
                "description": "Contact numbers and email addresses with use flags (Home, Work, Mobile).",
                "rules": "Strips 'tel:' or 'mailto:' URI schemes into structured system and value pairs."
            }
        ]
    },
    {
        "id": "allergies",
        "title": "Allergies & Adverse Reactions",
        "badge": "Clinical Section",
        "loinc": "48765-2",
        "cda_template": "2.16.840.1.113883.10.20.22.4.30 (Allergy Concern Act)",
        "description": "Captures patient substance allergies, drug intolerances, adverse reaction manifestations, and severity levels.",
        "xml_snippet": """<section>
  <templateId root="2.16.840.1.113883.10.20.22.2.6.1" extension="2015-08-01"/>
  <code code="48765-2" codeSystem="2.16.840.1.113883.6.1" displayName="Allergies and adverse reactions Document"/>
  <title>Allergies &amp; Alerts</title>
  <text><table>...</table></text>
  <entry typeCode="DRIV">
    <act classCode="ACT" moodCode="EVN">
      <templateId root="2.16.840.1.113883.10.20.22.4.30"/>
      <id root="36e3e930-7b14-11db-9fe1-0800200c9a66"/>
      <code code="CONC" codeSystem="2.16.840.1.113883.5.6"/>
      <statusCode code="active"/>
      <effectiveTime><low value="20100615"/></effectiveTime>
      <entryRelationship typeCode="SUBJ">
        <observation classCode="OBS" moodCode="EVN">
          <templateId root="2.16.840.1.113883.10.20.22.4.7"/>
          <code code="419199007" codeSystem="2.16.840.1.113883.6.96" displayName="Allergy to substance"/>
          <value xsi:type="CD" code="70618" codeSystem="2.16.840.1.113883.6.88" displayName="Penicillin G"/>
          <participant typeCode="CSM">
            <participantRole classCode="MANU">
              <playingEntity classCode="MMAT">
                <code code="70618" codeSystem="2.16.840.1.113883.6.88" displayName="Penicillin G"/>
              </playingEntity>
            </participantRole>
          </participant>
          <entryRelationship typeCode="MFST">
            <observation classCode="OBS" moodCode="EVN">
              <templateId root="2.16.840.1.113883.10.20.22.4.9"/>
              <value xsi:type="CD" code="247472004" codeSystem="2.16.840.1.113883.6.96" displayName="Hives"/>
              <entryRelationship typeCode="SUBJ">
                <observation classCode="OBS" moodCode="EVN">
                  <templateId root="2.16.840.1.113883.10.20.22.4.8"/>
                  <value xsi:type="CD" code="6736007" codeSystem="2.16.840.1.113883.6.96" displayName="Moderate"/>
                </observation>
              </entryRelationship>
            </observation>
          </entryRelationship>
        </observation>
      </entryRelationship>
    </act>
  </entry>
</section>""",
        "json_snippet": """{
  "sections": {
    "allergies": {
      "title": "Allergies & Alerts",
      "code": {
        "code": "48765-2",
        "code_system_name": "LOINC",
        "display_name": "Allergies and adverse reactions Document"
      },
      "entries": [
        {
          "substance": {
            "code": "70618",
            "code_system": "2.16.840.1.113883.6.88",
            "code_system_name": "RxNorm",
            "display_name": "Penicillin G"
          },
          "allergy_type": {
            "code": "419199007",
            "display_name": "Allergy to substance"
          },
          "status": "active",
          "effective_time": {
            "low": "2010-06-15"
          },
          "reactions": [
            {
              "reaction": {
                "code": "247472004",
                "code_system_name": "SNOMED CT",
                "display_name": "Hives"
              },
              "severity": {
                "code": "6736007",
                "code_system_name": "SNOMED CT",
                "display_name": "Moderate"
              }
            }
          ]
        }
      ]
    }
  }
}""",
        "fields": [
            {
                "xml_path": "observation/participant/.../playingEntity/code",
                "json_path": "allergies.entries[].substance",
                "data_type": "CD (Concept Descriptor)",
                "code_system": "RxNorm / UNII / NDF-RT",
                "description": "Coded substance or medication causing the allergic reaction.",
                "rules": "Falls back to observation/value if playingEntity is not present; resolves narrative reference if displayName is empty."
            },
            {
                "xml_path": "observation/code/@code",
                "json_path": "allergies.entries[].allergy_type",
                "data_type": "CD",
                "code_system": "SNOMED CT (2.16.840.1.113883.6.96)",
                "description": "Type of allergy (Allergy to drug, Food allergy, Environmental allergy, Intolerance).",
                "rules": "Extracts clinical type code and displayName."
            },
            {
                "xml_path": "act/statusCode/@code or observation/statusCode/@code",
                "json_path": "allergies.entries[].status",
                "data_type": "CS (Coded Simple)",
                "code_system": "HL7 ActStatus",
                "description": "Clinical status of the allergy concern (active, completed, inactive, resolved).",
                "rules": "Normalized to lowercase standard status string."
            },
            {
                "xml_path": "act/effectiveTime/low | observation/effectiveTime/low",
                "json_path": "allergies.entries[].effective_time.low",
                "data_type": "IVL_TS (Interval Timestamp)",
                "code_system": "ISO-8601 Date",
                "description": "Date of allergy onset or first observation.",
                "rules": "Standardized to ISO-8601 date string."
            },
            {
                "xml_path": "entryRelationship[@typeCode='MFST']/observation/value",
                "json_path": "allergies.entries[].reactions[].reaction",
                "data_type": "CD",
                "code_system": "SNOMED CT",
                "description": "Clinical reaction manifestation (e.g. Hives, Anaphylaxis, Wheezing, Rash).",
                "rules": "Traverses nested Reaction Observation template (2.16.840.1.113883.10.20.22.4.9)."
            },
            {
                "xml_path": "entryRelationship[@typeCode='SUBJ']/observation/value",
                "json_path": "allergies.entries[].reactions[].severity",
                "data_type": "CD",
                "code_system": "SNOMED CT",
                "description": "Severity assessment of the allergic reaction (Mild, Moderate, Severe, Fatal).",
                "rules": "Traverses nested Severity Observation template (2.16.840.1.113883.10.20.22.4.8)."
            }
        ]
    },
    {
        "id": "medications",
        "title": "Medications & Prescriptions",
        "badge": "Clinical Section",
        "loinc": "10160-0 / 29549-3",
        "cda_template": "2.16.840.1.113883.10.20.22.4.16 (Medication Activity)",
        "description": "Details prescribed, administered, or reported medications, doses, routes, frequencies, schedules, and indications.",
        "xml_snippet": """<substanceAdministration classCode="SBADM" moodCode="EVN">
  <templateId root="2.16.840.1.113883.10.20.22.4.16" extension="2014-06-09"/>
  <id root="6c844c75-aa34-411c-b7bd-5e4a9f20f882"/>
  <statusCode code="active"/>
  <effectiveTime xsi:type="IVL_TS">
    <low value="20200115"/>
  </effectiveTime>
  <effectiveTime xsi:type="PIVL_TS" institutionSpecified="true" operator="A">
    <period value="12" unit="h"/>
  </effectiveTime>
  <routeCode code="C38288" codeSystem="2.16.840.1.113883.3.26.1.1" codeSystemName="NCI" displayName="Oral"/>
  <doseQuantity value="500" unit="mg"/>
  <consumable>
    <manufacturedProduct classCode="MANU">
      <templateId root="2.16.840.1.113883.10.20.22.4.23"/>
      <manufacturedMaterial>
        <code code="860975" codeSystem="2.16.840.1.113883.6.88" displayName="Metformin hydrochloride 500 MG Oral Tablet"/>
      </manufacturedMaterial>
    </manufacturedProduct>
  </consumable>
  <entryRelationship typeCode="RSON">
    <observation classCode="OBS" moodCode="EVN">
      <templateId root="2.16.840.1.113883.10.20.22.4.19"/>
      <code code="404684003" codeSystem="2.16.840.1.113883.6.96" displayName="Clinical finding"/>
      <value xsi:type="CD" code="44054006" codeSystem="2.16.840.1.113883.6.96" displayName="Type 2 Diabetes Mellitus"/>
    </observation>
  </entryRelationship>
</substanceAdministration>""",
        "json_snippet": """{
  "medication": {
    "code": "860975",
    "code_system": "2.16.840.1.113883.6.88",
    "code_system_name": "RxNorm",
    "display_name": "Metformin hydrochloride 500 MG Oral Tablet"
  },
  "status": "active",
  "dose": {
    "value": 500.0,
    "unit": "mg",
    "formatted": "500 mg"
  },
  "route": {
    "code": "C38288",
    "display_name": "Oral"
  },
  "schedule": {
    "period": {
      "value": "12",
      "unit": "h",
      "human_readable": "Twice daily (q12h)"
    }
  },
  "date_range": {
    "low": "2020-01-15"
  },
  "indication": {
    "code": "44054006",
    "code_system_name": "SNOMED CT",
    "display_name": "Type 2 Diabetes Mellitus"
  }
}""",
        "fields": [
            {
                "xml_path": "consumable/.../manufacturedMaterial/code",
                "json_path": "medications.entries[].medication",
                "data_type": "CD (Concept Descriptor)",
                "code_system": "RxNorm (2.16.840.1.113883.6.88)",
                "description": "Standardized RxNorm clinical medication product, brand name, or generic ingredient.",
                "rules": "Extracts RxNorm code, system name, and resolves narrative text if displayName is omitted."
            },
            {
                "xml_path": "doseQuantity/@value + @unit",
                "json_path": "medications.entries[].dose",
                "data_type": "PQ (Physical Quantity)",
                "code_system": "UCUM (2.16.840.1.113883.6.8)",
                "description": "Amount of medication per administration (e.g. 500 mg, 10 mL, 2 puffs).",
                "rules": "Converts numeric string to float and generates formatted string helper (e.g. '500 mg')."
            },
            {
                "xml_path": "routeCode/@code + @displayName",
                "json_path": "medications.entries[].route",
                "data_type": "CE (Coded with Equiv)",
                "code_system": "NCI Thesaurus / FDA Route",
                "description": "Route of administration (Oral, Intravenous, Topical, Inhalation).",
                "rules": "Normalizes route codes to readable clinical terminology."
            },
            {
                "xml_path": "effectiveTime[xsi:type='PIVL_TS']/period",
                "json_path": "medications.entries[].schedule.period",
                "data_type": "PIVL_TS (Periodic Interval)",
                "code_system": "HL7 Timing",
                "description": "Dosage frequency interval (e.g. every 12 hours, daily, every 8 hours).",
                "rules": "Automatically translates numeric period + unit into standard clinical phrasing ('Twice daily (q12h)', 'Every 8 hours (q8h)')."
            },
            {
                "xml_path": "effectiveTime[xsi:type='IVL_TS']/low | high",
                "json_path": "medications.entries[].date_range",
                "data_type": "IVL_TS (Interval Timestamp)",
                "code_system": "ISO-8601 Date",
                "description": "Start and end dates of medication therapy.",
                "rules": "Parses low (start) and optional high (discontinue/stop) dates."
            },
            {
                "xml_path": "entryRelationship[@typeCode='RSON']/observation/value",
                "json_path": "medications.entries[].indication",
                "data_type": "CD",
                "code_system": "SNOMED CT / ICD-10",
                "description": "Clinical diagnosis or reason for medication prescription.",
                "rules": "Traverses nested Indication Observation template (2.16.840.1.113883.10.20.22.4.19)."
            }
        ]
    }
]

CODE_SYSTEMS = [
    {"name": "LOINC", "oid": "2.16.840.1.113883.6.1", "badge": "bg-blue-500/10 text-blue-400 border-blue-500/30", "desc": "Logical Observation Identifiers Names and Codes for Lab Tests, Vitals, Clinical Documents, and Section Headings."},
    {"name": "SNOMED CT", "oid": "2.16.840.1.113883.6.96", "badge": "bg-purple-500/10 text-purple-400 border-purple-500/30", "desc": "Systematized Nomenclature of Medicine for Clinical Findings, Diagnoses, Reactions, and Procedures."},
    {"name": "RxNorm", "oid": "2.16.840.1.113883.6.88", "badge": "bg-emerald-500/10 text-emerald-400 border-emerald-500/30", "desc": "NLM Standardized Clinical Drug Nomenclature for Medications, Ingredients, Forms, and Strengths."},
    {"name": "ICD-10-CM", "oid": "2.16.840.1.113883.6.3", "badge": "bg-amber-500/10 text-amber-400 border-amber-500/30", "desc": "International Classification of Diseases, Tenth Revision, Clinical Modification for Billing and Diagnoses."},
    {"name": "CVX", "oid": "2.16.840.1.113883.12.292", "badge": "bg-indigo-500/10 text-indigo-400 border-indigo-500/30", "desc": "CDC Vaccines Administered Code System for Immunization Tracking."},
    {"name": "CPT-4", "oid": "2.16.840.1.113883.6.12", "badge": "bg-rose-500/10 text-rose-400 border-rose-500/30", "desc": "Current Procedural Terminology for Medical, Surgical, and Diagnostic Procedures."},
    {"name": "UCUM", "oid": "2.16.840.1.113883.6.8", "badge": "bg-teal-500/10 text-teal-400 border-teal-500/30", "desc": "Unified Code for Units of Measure for Lab & Vital Sign Physical Quantities (mm[Hg], mg, /min, etc.)."}
]


def generate_html_dashboard(output_file: str) -> None:
    # Read the canonical template from docs/ccda_mapping_dashboard.html relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(project_root, "docs", "ccda_mapping_dashboard.html")
    
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        raise FileNotFoundError(f"Canonical dashboard template not found at {template_path}")

    out_abs = os.path.abspath(output_file)
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    with open(out_abs, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Interactive Dashboard generated successfully at: {output_file}")


def main():
    out = "docs/ccda_mapping_dashboard.html"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    generate_html_dashboard(out)


if __name__ == "__main__":
    main()
