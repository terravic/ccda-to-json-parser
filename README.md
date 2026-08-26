# C-CDA to JSON Parser and AI Skill

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20mandatory-brightgreen.svg)](#requirements)
[![HL7 C-CDA R2.1](https://img.shields.io/badge/HL7-C--CDA%20R2.1-orange.svg)](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=408)

A production-grade, zero-external-dependency Python engine and AI Skill that converts HL7 C-CDA (Consolidated Clinical Document Architecture) XML clinical documents into clean, structured, standardized JSON.

Ready for direct integration into enterprise AI assistants, Claude, OpenAI Agents, FastAPI, or any clinical data pipeline.

<p align="center">
  <img src="docs/images/ccda_skill_demo.jpg" alt="HL7 C-CDA to JSON Parser and Interactive Canvas UI Dashboard in Action" width="100%">
</p>

---

## Guide for Non-Technical Users

### What is C-CDA and Why Does It Need Converting?
When you visit a doctor, clinic, or hospital, the electronic health record (EHR) system records your health data: vital signs, active prescriptions, allergies, past diagnoses, and lab results. When health systems share these records with other hospitals or patient portals, they typically package them in a standard file format called **HL7 C-CDA** (Consolidated Clinical Document Architecture).

C-CDA files are written in XML, a complex computer format filled with technical tags, numerical identification codes, and nested references. While standard across healthcare systems, raw C-CDA files are difficult for humans to read and challenging for modern software or AI assistants to process directly.

This skill translates complicated C-CDA medical files into **JSON** (a clean, organized data format structured like an electronic form) and generates **interactive visual charts** that anyone can understand.

---

### How to Use This Skill Without Writing Code

#### 1. In an AI Assistant
If you are interacting with an AI assistant that has this skill enabled, you do not need to write code. You can talk to the assistant using everyday language:

- "Please convert this patient discharge summary into a structured summary."
- "What medications is this patient taking, and what are their active dosages?"
- "Show me all recorded allergies and reaction severities for this patient."
- "Generate a visual dashboard for this clinical document."

The assistant will run the parser behind the scenes and answer your questions directly or present an interactive visual dashboard in your workspace.

#### 2. Three Common Non-Technical Workflows

- **Scenario A: Reading a High-Level Patient Summary**
  If you have a clinical XML file and want a quick overview of patient demographics, diagnoses, and medication counts, run:
  ```bash
  python3 parse.py samples/sample_1_continuity_of_care_document.xml --summary
  ```
  This prints a clean, readable text summary directly in the terminal without technical XML tags.

- **Scenario B: Exporting Medical Tables to Microsoft Excel**
  If your team works in spreadsheets, you can automatically convert the medical records into CSV spreadsheet files:
  ```bash
  python3 parse.py samples/sample_1_continuity_of_care_document.xml --csv-export ./my_spreadsheets/
  ```
  This creates separate spreadsheet files (`medications.csv`, `allergies.csv`, `problems.csv`, `vital_signs.csv`, `lab_results.csv`) that open directly in Excel or Google Sheets.

- **Scenario C: Opening the Visual Dashboard in Your Browser**
  You can open an interactive patient dashboard or mapping matrix in any web browser (Chrome, Edge, Safari):
  - Open `docs/ccda_mapping_dashboard.html` to explore the complete clinical mapping rules, medical code dictionaries, and side-by-side XML-to-JSON transformations.
  - Open `docs/sample_1_patient_dashboard.html` to view an interactive patient chart with vital sign cards, medication schedules, condition badges, and light/dark display modes.

---

## Key Features

- **Comprehensive Clinical Coverage**:
  - **Patient Demographics**: Names, date of birth, gender, race, ethnicity, addresses, phone numbers, email addresses, languages, guardians, medical record numbers (MRNs), and provider organizations.
  - **Allergies & Intolerances**: Substance codes (RxNorm and UNII), reaction manifestations, severity ratings, clinical status, and onset dates.
  - **Medications**: Generic and brand names, RxNorm codes, dosage amounts, routes of administration, dosing schedules, date ranges, clinical indications, and patient instructions.
  - **Problems & Diagnoses**: SNOMED CT concepts with ICD-10-CM crosswalks, clinical status (active, resolved, inactive), onset dates, and age at onset.
  - **Vital Signs**: Blood pressure (systolic and diastolic), heart rate, respiratory rate, body temperature, body mass index (BMI), oxygen saturation (SpO2), height, and weight measurements with standard units.
  - **Diagnostic Labs & Results**: Chemistry panels, hematology panels, LOINC test codes, numeric values, reference ranges, and abnormal high/low flags.
  - **Immunizations**: CDC Vaccine Administered (CVX) codes, administration dates, lot numbers, routes, manufacturer names, and refusal reasons.
  - **Encounters & Clinical Visits**: Outpatient visits, hospital admissions, consultations, provider specialties, facility locations, and encounter diagnoses.
  - **Procedures**: Surgical and diagnostic procedures (CPT-4, SNOMED CT, ICD-10-PCS), procedure dates, performing clinicians, and anatomical target sites.
  - **Social History**: Standardized smoking status (NHIS codes), tobacco history, alcohol use, and social determinants of health.
  - **Plan of Care & Instructions**: Treatment plans, planned orders, follow-up appointments, and post-discharge patient instructions.
- **Robust XML Syntax Handling**:
  - Automatically handles XML namespaces (`urn:hl7-org:v3`, `sdtc:`, `xsi:`, `voc:`).
  - Resolves internal narrative references (`<reference value="#med1"/>`) to populate display names when coded attributes omit them.
  - Gracefully handles null flavor indicators (`UNK`, `NA`, `NI`, `ASKU`, `NASK`, `MSK`, `OTH`) without crashing.
  - Converts HL7 timestamp strings (`20230514143000-0500`, `20230514`) to standardized ISO-8601 dates and timestamps.
  - Extracts embedded HTML narrative tables (`<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`) into structured arrays.
- **Zero Mandatory Dependencies**: Built entirely on the Python Standard Library (`xml.etree.ElementTree`, `json`, `csv`, `re`, `datetime`). Runs in restricted, serverless, or offline environments without external package installations.
- **Flexible Interfaces**:
  - Python API (`import ccda_parser`)
  - Command Line Interface (CLI) with indentation formatting, batch folder processing, terminal summaries, CSV export, and HTML reports.
  - Standardized `SKILL.md` for AI agent platforms and tool integration systems.
  - Interactive Canvas UI dashboards with light and dark mode toggles.

---

## Repository Structure

```
ccda-to-json-parser/
├── LICENSE                                     # Apache 2.0 license file
├── README.md                                    # Project documentation and user guide
├── SKILL.md                                     # AI Agent and Gemini Enterprise Skill definition
├── parse.py                                     # Direct CLI executable runner script
├── pyproject.toml                               # Modern package build configuration
├── requirements.txt                             # Python dependencies (standard library first)
├── setup.py                                     # Setup configuration for pip installation
├── docs/
│   ├── ccda_mapping_dashboard.html              # Interactive Canvas UI mapping matrix dashboard
│   ├── sample_1_patient_dashboard.html          # Sample patient interactive visual dashboard
│   └── images/
│       └── ccda_skill_demo.jpg                  # Header demonstration graphic
├── samples/
│   ├── sample_1_continuity_of_care_document.xml # Synthetic outpatient CCD
│   ├── sample_2_discharge_summary.xml          # Synthetic inpatient discharge summary
│   ├── sample_3_cardiology_referral_note.xml   # Synthetic cardiology referral note
│   └── converted_json/
│       ├── sample_1_continuity_of_care_document.json # Pre-converted CCD JSON output
│       ├── sample_2_discharge_summary.json     # Pre-converted discharge summary JSON output
│       └── sample_3_cardiology_referral_note.json # Pre-converted referral note JSON output
├── scripts/
│   ├── convert_all_samples.py                   # Batch sample conversion utility script
│   ├── generate_mapping_dashboard.py            # Mapping matrix dashboard HTML generator
│   └── validate_ccda.py                         # C-CDA XML structural conformance validator
├── src/
│   └── ccda_parser/
│       ├── __init__.py                          # Public package API and version exports
│       ├── __main__.py                          # Executable module entry point
│       ├── cli.py                               # Command-line interface with parsing flags
│       ├── models.py                            # Structured data models and type definitions
│       ├── parser.py                            # Core C-CDA XML parsing engine
│       ├── visualizer.py                        # HTML Canvas visual report generator
│       ├── sections/                            # Modular clinical domain section extractors
│       │   ├── __init__.py                      # Section classifier and dispatch router
│       │   ├── allergies.py                     # Allergies and adverse reactions extractor
│       │   ├── encounters.py                    # Clinical encounters and visits extractor
│       │   ├── generic_section.py               # Fallback extractor for custom narrative sections
│       │   ├── header.py                        # Patient demographics and document header metadata
│       │   ├── immunizations.py                 # Vaccines and immunization history extractor
│       │   ├── medications.py                   # Medications and prescription extractor
│       │   ├── problems.py                      # Problem list, conditions, and diagnoses extractor
│       │   ├── procedures.py                    # Surgical and diagnostic procedures extractor
│       │   ├── results.py                       # Diagnostic tests and laboratory panels extractor
│       │   ├── social_history.py                # Smoking status and social history extractor
│       │   └── vital_signs.py                   # Vital signs and physiological panels extractor
│       └── utils/                               # Parsing utility helper modules
│           ├── __init__.py                      # Utility package initialization
│           ├── code_utils.py                    # Medical terminology and OID resolution
│           ├── date_utils.py                    # HL7 timestamp conversion to ISO-8601
│           ├── narrative_utils.py               # Narrative text, tables, and reference lookups
│           └── xml_utils.py                     # XML namespace and element traversal helpers
└── tests/
    ├── __init__.py                              # Test suite package initialization
    ├── test_parser.py                           # Unit tests for parser utilities and models
    └── test_samples.py                          # End-to-end verification tests on sample files
```

---

## Quick Start

### 1. Python Library Usage

```python
from ccda_parser import parse_ccda, parse_ccda_file

# Parse a C-CDA XML file
data = parse_ccda_file("samples/sample_1_continuity_of_care_document.xml")

# Patient Information
print(data["patient"]["name"]["full_name"])       # "Ms. Eleanor Marie Vance"
print(data["patient"]["birth_time"])              # "1975-08-22"
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
# Basic conversion to standard output
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

# Generate an interactive Canvas UI HTML patient dashboard
python3 parse.py samples/sample_1_continuity_of_care_document.xml --html-report patient_dashboard.html

# Open or generate the C-CDA to JSON Mapping Matrix visual dashboard
python3 parse.py --mapping-dashboard docs/ccda_mapping_dashboard.html
```

---

## Interactive Canvas UI and Visual Dashboards

This skill provides rich, interactive Canvas UI elements designed for AI agent platforms and web browser environments:

1. **C-CDA to JSON Mapping Matrix Dashboard (`docs/ccda_mapping_dashboard.html`)**:
   - **Interactive Clinical Explorer**: Visual exploration of all 12 clinical domains (Demographics, Allergies, Medications, Problems, Vitals, Labs, Immunizations, Encounters, Procedures, Social History, Care Plan, and Generic Sections).
   - **Side-by-Side Live Transformation**: Direct visual link between source HL7 C-CDA XML snippets and target normalized JSON structures.
   - **Field-by-Field Rules**: Detailed breakdown of XPath expressions, data types (`PQ`, `CD`, `IVL_TS`, `ST`), vocabulary systems (LOINC, SNOMED CT, RxNorm, CVX, ICD-10), and null flavor resilience.
   - **Live Keyword Search & Filter**: Real-time cross-section search.
   - **Light/Dark Display Toggle**: High-contrast, professional health-tech user interface.

2. **Patient Visual Dashboard Generator (`--html-report`)**:
   - Generates an executive patient report with vital signs cards, active medication badges, problem lists, allergy alerts, and collapsible raw JSON inspection.

---

## JSON Output Schema

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

## Testing and Verification

Run the test suite to verify that all components function properly:

```bash
# Run all unit tests and sample validation tests
python3 -m unittest discover -s tests -p "test_*.py" -v

# Batch convert all sample files
python3 scripts/convert_all_samples.py

# Validate XML conformance for any C-CDA file
python3 scripts/validate_ccda.py samples/sample_1_continuity_of_care_document.xml
```

---

## Synthetic Sample Files

The repository includes 3 realistic, synthetic clinical documents:

1. **`sample_1_continuity_of_care_document.xml`**: Comprehensive outpatient CCD record for Eleanor Vance with Type 2 Diabetes, Hypertension, Hyperlipidemia, active medications, allergies (Penicillin, Peanut), lab results (HbA1c 6.8%, Lipid panel), vitals, immunizations, and care plan.
2. **`sample_2_discharge_summary.xml`**: Hospital inpatient discharge summary for Marcus Thorne following laparoscopic appendectomy, featuring hospital course narrative, discharge medications, post-operative care instructions, and sulfa allergy.
3. **`sample_3_cardiology_referral_note.xml`**: Specialist consultation note for Sophia Rodriguez presenting with palpitations and heart murmur, including physical exam, vital signs, outpatient encounter billing codes, and diagnostic orders (Holter ECG, Echocardiogram).

---

## License

This project is licensed under the **Apache License 2.0**.
