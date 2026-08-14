# C-CDA to JSON Parser & AI Skill

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20mandatory-brightgreen.svg)](#requirements)
[![HL7 C-CDA R2.1](https://img.shields.io/badge/HL7-C--CDA%20R2.1-orange.svg)](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=408)

A production-grade, zero-external-dependency Python engine and AI Skill that converts **HL7 C-CDA (Consolidated Clinical Document Architecture) XML** clinical documents into clean, structured, standardized **JSON**.

Ready for direct integration into **GitHub**, **Gemini Enterprise**, **Jetski**, **Claude**, **OpenAI Agents**, **FastAPI**, or any clinical data pipeline.

---

## 🌟 Key Features

- **Comprehensive Clinical Coverage**:
  - **Patient Demographics**: Names, DOB, Gender, Race, Ethnicity, Addresses, Telecoms, Languages, Guardians, MRN/IDs, Provider Orgs.
  - **Allergies & Intolerances**: Substance codes (RxNorm/UNII), Reactions, Severity, Clinical Status, Onset dates.
  - **Medications**: Generic/Brand names, RxNorm codes, Dosage, Route, Frequency/Schedule (`PIVL_TS`), Date ranges, Indications, Instructions.
  - **Problems & Diagnoses**: SNOMED CT and ICD-10-CM codes, Clinical status, Onset dates, Age at onset.
  - **Vital Signs**: BP (Systolic/Diastolic), Heart Rate, Respiratory Rate, Temp, BMI, SpO2, Heights, Weights, and Panels.
  - **Diagnostic Labs & Results**: Lab panels, LOINC codes, Numeric values (`PQ`), Reference ranges, Normal/High/Low interpretations.
  - **Immunizations**: Vaccine products (CVX), Dates, Lot numbers, Route/Site, Refusal/Negation reasons.
  - **Encounters & Visits**: Outpatient, Inpatient, Emergency visits, Performers, Facilities, Encounter diagnoses.
  - **Procedures**: Surgical & Diagnostic procedures (CPT-4, SNOMED, ICD-10-PCS), Dates, Surgeons, Implanted devices.
  - **Social History**: Smoking status (LOINC 72166-2), Tobacco use, Alcohol use, Social determinants.
  - **Plan of Care / Hospital Course / Assessment & Plan / Discharge Instructions**: Structured narratives and actionable plans.
- **Robust XML Syntax Handling**:
  - Automatically handles XML namespaces (`urn:hl7-org:v3`, `sdtc:`, `xsi:`, `voc:`).
  - Resolves internal narrative references (`<reference value="#med1"/>`) to populate display names when codes lack them.
  - Gracefully handles `nullFlavor` codes (`UNK`, `NA`, `NI`, `ASKU`) without crashing.
  - Converts HL7 timestamp strings (`20230514143000-0500`, `20230514`) to standard **ISO-8601** format.
  - Parses embedded HTML narrative tables (`<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`) into structured JSON arrays of objects.
- **Zero Mandatory Dependencies**: Built 100% on the Python Standard Library (`xml.etree.ElementTree`, `json`, `csv`, `re`, `datetime`). Runs in any restricted, air-gapped, or serverless environment without `pip install` blockers.
- **Flexible Interfaces**:
  - Simple Python API (`import ccda_parser`)
  - Rich CLI with pretty-printing, directory batch conversion, clinical summaries, and CSV table exports.
  - Standardized `SKILL.md` for Gemini Enterprise, Jetski, and LLM agent plugin systems.

---

## 📂 Repository Structure

```
ccda-to-json-parser/
├── SKILL.md                          # AI Agent & Gemini Enterprise Skill definition
├── README.md                         # Project documentation and API guide
├── requirements.txt                  # Python dependencies (stdlib-first)
├── pyproject.toml                    # Modern package build configuration
├── setup.py                          # Setup configuration for pip
├── parse.py                          # Direct CLI runner script
├── src/
│   └── ccda_parser/
│       ├── __init__.py               # Public API exports
│       ├── __main__.py               # Module runner (python3 -m ccda_parser)
│       ├── cli.py                    # Command-line interface with flags
│       ├── parser.py                 # Core C-CDA parser engine
│       ├── models.py                 # Dataclasses and JSON schema models
│       ├── sections/                 # Modular domain section parsers
│       │   ├── __init__.py           # Section classifier and dispatch router
│       │   ├── header.py             # Demographics, metadata, authors, encounters
│       │   ├── allergies.py          # Allergies & Intolerances
│       │   ├── medications.py        # Medications & Prescriptions
│       │   ├── problems.py           # Problem list & Conditions
│       │   ├── immunizations.py      # Vaccines & Administration
│       │   ├── vital_signs.py        # Vital signs & Panels
│       │   ├── results.py            # Lab tests & Diagnostic panels
│       │   ├── encounters.py         # Encounters & Visits
│       │   ├── procedures.py         # Procedures & Devices
│       │   ├── social_history.py     # Smoking & Social history
│       │   └── generic_section.py    # Fallback parser for any custom section
│       └── utils/
│           ├── __init__.py
│           ├── xml_utils.py          # Namespace stripping & element traversal
│           ├── date_utils.py         # HL7 TS/IVL to ISO-8601 formatting
│           ├── code_utils.py         # OID terminology resolution & value parsing
│           └── narrative_utils.py    # Narrative cleanup, tables, & ID refs
├── samples/
│   ├── sample_1_continuity_of_care_document.xml    # Synthetic Outpatient CCD
│   ├── sample_2_discharge_summary.xml             # Synthetic Inpatient Discharge Summary
│   ├── sample_3_cardiology_referral_note.xml      # Synthetic Specialist Referral Note
│   └── converted_json/                            # Pre-generated converted JSON files
├── tests/
│   ├── __init__.py
│   ├── test_parser.py                # Unit tests for parser utilities
│   └── test_samples.py               # End-to-end tests for all 3 sample files
└── scripts/
    ├── convert_all_samples.py        # Batch sample conversion utility
    └── validate_ccda.py              # C-CDA XML structural conformance validator
```

---

## 🚀 Quick Start

### 1. Python Library Usage

```python
from ccda_parser import parse_ccda, parse_ccda_file

# Parse a C-CDA XML file
data = parse_ccda_file("samples/sample_1_continuity_of_care_document.xml")

# Patient Information
print(data["patient"]["name"]["full_name"])  # "Ms. Eleanor Marie Vance"
print(data["patient"]["birth_time"])         # "1975-08-22"
print(data["patient"]["gender"]["display_name"])  # "Female"

# Active Medications
for med in data["sections"]["medications"]["entries"]:
    name = med["medication"]["display_name"]
    dose = med["dose"]["formatted"]
    status = med["status"]
    print(f"- {name} ({dose}) [{status}]")

# Lab Results
for lab in data["sections"]["results"]["results"]:
    test = lab["test"]["display_name"]
    val = lab["value"]["value"]
    unit = lab["value"]["unit"]
    interp = lab.get("interpretation", {}).get("display_name", "Normal")
    print(f"- {test}: {val} {unit} ({interp})")
```

### 2. Command Line Usage

```bash
# Basic conversion to stdout
python3 parse.py samples/sample_1_continuity_of_care_document.xml

# Save formatted JSON to file
python3 parse.py samples/sample_1_continuity_of_care_document.xml -o output.json --pretty

# Batch convert an entire folder of C-CDA XML files
python3 parse.py ./samples/ -o ./json_output/ --pretty

# Display human-readable clinical summary in terminal
python3 parse.py samples/sample_1_continuity_of_care_document.xml --summary

# Extract specific sections only
python3 parse.py samples/sample_1_continuity_of_care_document.xml --sections allergies,medications,problems -o filtered.json

# Export clinical tables directly to CSV files
python3 parse.py samples/sample_1_continuity_of_care_document.xml --csv-export ./csv_out/
```

---

## 📊 JSON Output Schema

Below is an overview of the structured output schema:

```json
{
  "document_meta": {
    "title": "Continuity of Care Document (CCD)",
    "document_type": {
      "code": "34133-9",
      "code_system_name": "LOINC",
      "display_name": "Summarization of Episode Note"
    },
    "effective_time": "2023-05-14T14:30:00-05:00",
    "confidentiality": {"code": "N", "display_name": "Normal"},
    "authors": [...],
    "custodian": {...}
  },
  "patient": {
    "name": {
      "full_name": "Ms. Eleanor Marie Vance",
      "first_name": "Eleanor",
      "last_name": "Vance"
    },
    "birth_time": "1975-08-22",
    "gender": {"code": "F", "display_name": "Female"},
    "race": {"code": "2106-3", "display_name": "White"},
    "ethnicity": {"code": "2186-5", "display_name": "Not Hispanic or Latino"},
    "addresses": [...],
    "telecoms": [...]
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
    "available_sections": ["allergies", "medications", "problems", "vital_signs", "results", "immunizations", "social_history", "plan_of_care"]
  },
  "sections": {
    "allergies": {
      "title": "Allergies, Adverse Reactions & Alerts",
      "narrative": "...",
      "tables": [...],
      "entries": [...]
    },
    "medications": {
      "title": "Medications",
      "narrative": "...",
      "tables": [...],
      "entries": [...]
    },
    "problems": {
      "title": "Problems & Health Conditions",
      "entries": [...]
    },
    "vital_signs": {
      "title": "Vital Signs",
      "panels": [...],
      "measurements": [...]
    },
    "results": {
      "title": "Diagnostic Results & Laboratory Data",
      "panels": [...],
      "results": [...]
    }
  }
}
```

---

## 🧪 Testing & Verification

Run the test suite to verify everything works seamlessly:

```bash
# Run all unit tests and sample validation tests
python3 -m unittest discover -s tests -p "test_*.py" -v

# Batch convert all sample files
python3 scripts/convert_all_samples.py

# Validate XML conformance for any C-CDA file
python3 scripts/validate_ccda.py samples/sample_1_continuity_of_care_document.xml
```

---

## 📋 Synthetic Sample Files

The repository includes 3 realistic, synthetic clinical documents:

1. **`sample_1_continuity_of_care_document.xml`**: Comprehensive outpatient CCD record for Eleanor Vance with Type 2 Diabetes, Hypertension, Hyperlipidemia, active medications, allergies (Penicillin, Peanut), lab results (HbA1c 6.8%, Lipid panel), vitals, immunizations, and care plan.
2. **`sample_2_discharge_summary.xml`**: Hospital inpatient discharge summary for Marcus Thorne following laparoscopic appendectomy, featuring hospital course narrative, discharge medications, post-operative care instructions, and sulfa allergy.
3. **`sample_3_cardiology_referral_note.xml`**: Specialist consultation note for Sophia Rodriguez presenting with palpitations and heart murmur, including physical exam, vital signs, outpatient encounter billing codes, and diagnostic orders (Holter ECG, Echocardiogram).

---

## 📜 License

This project is licensed under the **Apache License 2.0**.
