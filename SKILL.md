---
name: ccda-to-json-parser
description: Accepts HL7 C-CDA (Consolidated Clinical Document Architecture) XML files, parses all header metadata and clinical sections (Allergies, Medications, Problems, Vitals, Labs, Encounters, Procedures, Immunizations, Social History, Plan of Care), handles XML syntax variations (namespaces, null flavors, narrative references), and outputs structured, standardized JSON.
author: clinical-data-engineering
version: 1.0.0
tags:
  - healthcare
  - ccda
  - hl7
  - clinical-data
  - json-converter
  - ehr
  - emr
---

# C-CDA to JSON Parser Skill

This skill provides automated parsing and transformation of **HL7 C-CDA (Consolidated Clinical Document Architecture) R1.1 / R2.0 / R2.1 XML documents** into clean, standardized, developer-friendly **JSON format**.

It handles all document types—including **Continuity of Care Documents (CCD)**, **Discharge Summaries**, **Consultation & Referral Notes**, **Care Plans**, **Progress Notes**, and **History & Physical (H&P) Notes**—while robustly resolving XML namespaces, null flavors, narrative text references, and complex coded terminology (LOINC, SNOMED CT, RxNorm, ICD-10-CM, CPT-4, CVX).

---

## When to Use This Skill

Use this skill whenever you need to:
1. **Ingest and convert clinical XML files** (`.xml`, `.ccda`, `.cda`) into structured JSON for LLM summarization, downstream EHR analytics, FHIR pipeline ingestion, or database persistence.
2. **Extract structured clinical domains**:
   - **Patient Demographics** (Names, DOB, Administrative Gender, Race, Ethnicity, Address, Telecom, Guardians, MRN/IDs)
   - **Allergies & Intolerances** (Substance, Reaction manifestations, Severity, Clinical Status, Onset)
   - **Medications** (Medication names, RxNorm codes, Dosage, Route, Timing/Frequency intervals, Status, Indications, Instructions)
   - **Problems & Conditions** (Problem description, SNOMED / ICD-10 codes, Status, Onset date, Age at onset)
   - **Vital Signs** (Systolic/Diastolic BP, Heart Rate, Respiratory Rate, Body Temperature, SpO2, Height, Weight, BMI)
   - **Diagnostic Results / Labs** (Lab Panels, Test Names, LOINC codes, Result values & units, Reference ranges, Interpretations)
   - **Immunizations** (Vaccines, CVX codes, Administration date, Lot numbers, Refusal reasons)
   - **Encounters & Visits** (Encounter types, Dates, Providers, Locations, Encounter diagnoses)
   - **Procedures** (Surgical/diagnostic procedures, CPT codes, Dates, Surgeons, Devices)
   - **Social History** (Smoking status, Tobacco use, Alcohol, Social determinants)
   - **Plan of Care / Hospital Course / Assessment & Plan / Discharge Instructions**
3. **Normalize legacy HL7 timestamp formats** (`YYYYMMDDHHMMSS-ZZZZ`, `YYYYMMDD`) into standard ISO-8601 strings.
4. **Generate clean clinical summaries or CSV table exports** from complex CDA XML files.

---

## Quick Execution Guide

### Option 1: Python CLI Command
Run the bundled CLI tool directly from shell:

```bash
# Convert single file to formatted JSON
python3 parse.py path/to/clinical_document.xml -o output.json --pretty

# Batch convert an entire directory of XML files
python3 parse.py ./samples/ -o ./json_output/ --pretty

# Output high-level clinical summary to console
python3 parse.py path/to/clinical_document.xml --summary

# Extract specific sections only
python3 parse.py path/to/clinical_document.xml --sections allergies,medications,problems -o filtered.json

# Export clinical tables to CSV format
python3 parse.py path/to/clinical_document.xml --csv-export ./csv_tables/

# Generate an interactive HTML patient report dashboard (with dual Input XML & Output JSON viewers)
python3 parse.py path/to/clinical_document.xml --html-report patient_dashboard.html

# Open or generate the C-CDA to JSON Mapping Matrix visual dashboard
python3 parse.py --mapping-dashboard docs/ccda_mapping_dashboard.html
```

### Option 2: Python Library API
Use programmatically in scripts or agent tools:

```python
from ccda_parser import parse_ccda, parse_ccda_file

# Parse directly from file path
clinical_data = parse_ccda_file("samples/sample_1_continuity_of_care_document.xml")

# Or parse raw XML string content
xml_content = open("document.xml").read()
clinical_data = parse_ccda(xml_content)

# Access patient demographics
print(clinical_data["patient"]["name"]["full_name"])
print(clinical_data["patient"]["birth_time"])

# Access structured sections
for med in clinical_data["sections"]["medications"]["entries"]:
    print(f"Medication: {med['medication']['display_name']} - Dose: {med['dose']['formatted']}")

# Access clinical summary counts
print(clinical_data["summary"]["counts"])
```

---

## JSON Output Structure Specification

The resulting JSON adheres to a clean, hierarchical schema:

```json
{
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
      "code_system": "2.16.840.1.113883.5.25",
      "display_name": "Normal"
    },
    "language": "en-US",
    "template_ids": [
      "2.16.840.1.113883.10.20.22.1.1:2015-08-01",
      "2.16.840.1.113883.10.20.22.1.2:2015-08-01"
    ],
    "authors": [
      {
        "time": "2023-05-14T14:30:00-05:00",
        "person": {
          "full_name": "Dr. Robert Sterling MD",
          "first_name": "Robert",
          "last_name": "Sterling"
        },
        "organization": {
          "name": "Metropolitan Health Outpatient Clinic"
        }
      }
    ],
    "custodian": {
      "name": "Metropolitan Health System"
    }
  },
  "patient": {
    "ids": [
      {
        "root": "2.16.840.1.113883.19.5",
        "extension": "MRN-8849201",
        "assigningAuthorityName": "Metropolitan Health System"
      }
    ],
    "name": {
      "full_name": "Ms. Eleanor Marie Vance",
      "first_name": "Eleanor",
      "middle_names": ["Marie"],
      "last_name": "Vance",
      "prefixes": ["Ms."]
    },
    "gender": {
      "code": "F",
      "code_system": "2.16.840.1.113883.5.1",
      "display_name": "Female"
    },
    "birth_time": "1975-08-22",
    "marital_status": {
      "code": "M",
      "display_name": "Married"
    },
    "race": {
      "code": "2106-3",
      "display_name": "White"
    },
    "ethnicity": {
      "code": "2186-5",
      "display_name": "Not Hispanic or Latino"
    },
    "addresses": [
      {
        "street_address_lines": ["742 Evergreen Terrace"],
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62704",
        "country": "US",
        "formatted": "742 Evergreen Terrace, Springfield, IL 62704, US"
      }
    ],
    "telecoms": [
      {"system": "tel", "value": "+1-555-733-4001", "use": "HP"},
      {"system": "mailto", "value": "eleanor.vance@example.org", "use": "HP"}
    ]
  },
  "summary": {
    "patient_name": "Ms. Eleanor Marie Vance",
    "date_of_birth": "1975-08-22",
    "gender": "Female",
    "counts": {
      "allergies": 2,
      "medications": 3,
      "problems": 2,
      "immunizations": 1,
      "vital_signs": 3,
      "lab_results": 1,
      "encounters": 0,
      "procedures": 0
    },
    "available_sections": [
      "allergies",
      "medications",
      "problems",
      "vital_signs",
      "results",
      "immunizations",
      "social_history",
      "plan_of_care"
    ]
  },
  "sections": {
    "allergies": {
      "title": "Allergies, Adverse Reactions & Alerts",
      "code": {"code": "48765-2", "code_system_name": "LOINC", "display_name": "Allergies and adverse reactions Document"},
      "narrative": "...",
      "tables": [...],
      "entries": [
        {
          "substance": {
            "code": "70618",
            "code_system": "2.16.840.1.113883.6.88",
            "code_system_name": "RxNorm",
            "display_name": "Penicillin G"
          },
          "allergy_type": {"code": "419199007", "display_name": "Allergy to substance"},
          "status": "active",
          "effective_time": {"low": "2010-06-15"},
          "reactions": [
            {
              "reaction": {"code": "247472004", "display_name": "Hives"},
              "severity": {"code": "6736007", "display_name": "Moderate"}
            }
          ]
        }
      ]
    },
    "medications": {
      "title": "Medications",
      "entries": [
        {
          "medication": {
            "code": "860975",
            "code_system_name": "RxNorm",
            "display_name": "Metformin hydrochloride 500 MG Oral Tablet"
          },
          "status": "active",
          "dose": {"value": 500.0, "unit": "mg", "formatted": "500 mg"},
          "route": {"code": "C38288", "display_name": "Oral"},
          "schedule": {"period": {"value": "12", "unit": "h", "human_readable": "Twice daily (q12h)"}},
          "date_range": {"low": "2020-01-15"},
          "indication": {"code": "44054006", "display_name": "Type 2 Diabetes Mellitus"}
        }
      ]
    },
    "problems": {
      "title": "Problems & Health Conditions",
      "entries": [
        {
          "problem": {
            "code": "44054006",
            "code_system_name": "SNOMED CT",
            "display_name": "Type 2 Diabetes Mellitus",
            "translations": [
              {"code": "E11.9", "code_system_name": "ICD-10-CM", "display_name": "Type 2 diabetes mellitus without complications"}
            ]
          },
          "status": "active",
          "effective_time": {"low": "2020-01-15"}
        }
      ]
    },
    "vital_signs": {
      "title": "Vital Signs",
      "panels": [
        {
          "panel_name": "Vital signs",
          "date": "2023-05-14T14:00:00-05:00",
          "measurements": [
            {
              "vital_sign": {"code": "8480-6", "display_name": "Systolic blood pressure"},
              "value": {"type": "PQ", "value": 128.0, "unit": "mm[Hg]"}
            },
            {
              "vital_sign": {"code": "8462-4", "display_name": "Diastolic blood pressure"},
              "value": {"type": "PQ", "value": 82.0, "unit": "mm[Hg]"}
            }
          ]
        }
      ]
    },
    "results": {
      "title": "Diagnostic Results & Laboratory Data",
      "results": [
        {
          "test": {"code": "4548-4", "display_name": "Hemoglobin A1c"},
          "value": {"type": "PQ", "value": 6.8, "unit": "%"},
          "interpretation": {"code": "H", "display_name": "High"},
          "reference_range": {"type": "IVL_PQ", "low": {"value": 4.0, "unit": "%"}, "high": {"value": 5.6, "unit": "%"}}
        }
      ]
    }
  }
}
```

---

## How It Handles XML Syntax Variations

1. **Namespaces**: Seamlessly strips or resolves default (`urn:hl7-org:v3`), extension (`urn:hl7-org:sdtc`), and prefix variations (`sdtc:`, `xsi:`, `voc:`, `v3:`).
2. **Missing Coded Names**: When a code's `displayName` is omitted in the XML entry, the parser automatically:
   - Resolves `<originalText><reference value="#refId"/></originalText>` from the section's narrative table/content.
   - Fallbacks to internal OID dictionary mappings for known standard codes.
3. **Null Flavors**: Properly handles HL7 null values (`UNK`, `NA`, `NI`, `ASKU`, `NASK`, `MSK`, `OTH`) without crashing or producing null pointer errors.
4. **Data Types**: Parses physical quantities (`PQ`), coded descriptors (`CD`, `CE`, `CV`, `CS`), strings (`ST`), booleans (`BL`), intervals (`IVL_TS`, `IVL_PQ`), and periodic frequencies (`PIVL_TS`).
5. **Custom / Unknown Sections**: Any unrecognized section in the C-CDA body is automatically captured via the `generic_section` parser, extracting its narrative text, HTML tables, and embedded clinical statements.

---

## Bundled Sample Files

The skill repository includes 3 realistic, synthetic C-CDA XML files for testing and verification:

1. `samples/sample_1_continuity_of_care_document.xml`: Comprehensive outpatient Continuity of Care Document (CCD) for a patient with Type 2 Diabetes, Hypertension, Hyperlipidemia, active medications, allergies, labs (HbA1c, Lipids), vitals, immunizations, and care plan.
2. `samples/sample_2_discharge_summary.xml`: Inpatient hospital discharge summary for a patient who underwent laparoscopic appendectomy, featuring hospital course narrative, admission/discharge diagnoses, discharge medications, post-op instructions, and allergies.
3. `samples/sample_3_cardiology_referral_note.xml`: Specialist cardiology referral note with reason for referral, cardiovascular physical exam, vital signs, outpatient consultation billing encounter, and ordered diagnostics (Holter monitor, Echocardiogram).

---

---

## Interactive Visual Dashboards

This skill includes full support for **interactive web dashboards** designed for modern web browsers and clinical data viewers.

### Runtime Architecture & Styling
- **Self-Contained HTML5**: Dashboards render standalone HTML5 / CSS / JavaScript with no mandatory backend server needed.
- **Allowed Styling Assets**: Tailwind CSS is loaded for responsive styling and high-contrast clinical dashboards:
  ```html
  <script src="https://cdn.tailwindcss.com"></script>
  ```
- **Theme Support & Light/Dark Mode**: High-contrast dark and light theme options with accessible contrast ratios.

---

### Included Visual Dashboards

#### 1. C-CDA to JSON Mapping Matrix Dashboard (`docs/ccda_mapping_dashboard.html`)
An interactive, enterprise-grade mapping explorer providing:
- **12 Clinical Section Deep-Dives**: Header/Demographics, Allergies, Medications, Problems, Vitals, Results/Labs, Immunizations, Encounters, Procedures, Social History, Plan of Care, and Generic Narrative Sections.
- **Side-by-Side Visual Transformation**: Real-time comparison between source HL7 C-CDA XML and target normalized JSON.
- **Field-by-Field Conversion Rules**: XPath expressions, JSON target properties, HL7 data types (`PQ`, `CD`, `IVL_TS`, `ST`), standard vocabularies, and null flavor fallback strategies.
- **Live Search & Filter**: Real-time keyword filtering across all XML paths, JSON fields, and LOINC codes.
- **Terminology Matrix**: Integrated OID registry for LOINC, SNOMED CT, RxNorm, ICD-10-CM, CVX, CPT-4, and UCUM.
- **Light/Dark Display Toggle**: Business-like, high-contrast, polished interface.

To view or regenerate the Mapping Matrix Dashboard:
```bash
python3 parse.py --mapping-dashboard docs/ccda_mapping_dashboard.html
```

#### 2. Dynamic Patient Clinical Dashboard (`parse.py --html-report`)
Transforms any parsed patient XML document into an executive interactive visual report with metric counters, clinical alerts, active medication cards, condition timelines, vital sign panels, dual input XML & output JSON viewers, and clinical domain tables:
```bash
python3 parse.py samples/sample_1_continuity_of_care_document.xml --html-report patient_dashboard.html
```

---

## Verification & Testing

To verify the parser in your environment:

```bash
# Run unit and end-to-end tests
python3 -m unittest discover -s tests -p "test_*.py" -v

# Run batch sample converter
python3 scripts/convert_all_samples.py

# Validate C-CDA XML conformance
python3 scripts/validate_ccda.py samples/sample_1_continuity_of_care_document.xml

# Generate Mapping Matrix Dashboard
python3 scripts/generate_mapping_dashboard.py docs/ccda_mapping_dashboard.html
```
