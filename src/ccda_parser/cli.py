"""
Command-line interface (CLI) for C-CDA to JSON Converter.
"""

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, List

# Support standalone execution
if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ccda_parser.parser import CCDAParser, parse_ccda_file
else:
    from .parser import CCDAParser, parse_ccda_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert HL7 C-CDA XML clinical documents to structured JSON format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ccda-parser input.xml
  ccda-parser input.xml -o output.json --pretty
  ccda-parser ./samples/ -o ./json_output/ --pretty
  ccda-parser input.xml --sections allergies,medications,problems
  ccda-parser input.xml --summary
  ccda-parser input.xml --csv-export ./csv_tables/
        """,
    )

    parser.add_argument(
        "input",
        help="Path to C-CDA XML file or directory containing XML files.",
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to output JSON file (or output directory if input is a directory). Default: stdout",
    )
    parser.add_argument(
        "-p", "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON with 2-space indentation (default: True).",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact JSON without indentation.",
    )
    parser.add_argument(
        "-s", "--sections",
        help="Comma-separated list of sections to include in output (e.g., allergies,medications,problems).",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a human-readable clinical summary to stderr/stdout.",
    )
    parser.add_argument(
        "--csv-export",
        metavar="DIR",
        help="Export parsed clinical sections (allergies, meds, vitals, labs, problems) to CSV files in DIR.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode (fail on any malformed XML section).",
    )

    args = parser.parse_args()

    input_path = args.input
    indent = None if args.compact else 2

    # Filter sections if specified
    filter_sections = [s.strip().lower() for s in args.sections.split(",")] if args.sections else None

    # Handle Directory or Single File
    if os.path.isdir(input_path):
        xml_files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.lower().endswith((".xml", ".ccda", ".cda"))
        ]
        if not xml_files:
            print(f"No XML files found in directory: {input_path}", file=sys.stderr)
            return 1

        out_dir = args.output or "./parsed_json_output"
        os.makedirs(out_dir, exist_ok=True)

        for xml_file in sorted(xml_files):
            try:
                data = parse_ccda_file(xml_file, strict=args.strict)
                if filter_sections:
                    data["sections"] = {k: v for k, v in data["sections"].items() if k.lower() in filter_sections}

                base_name = os.path.splitext(os.path.basename(xml_file))[0]
                out_file = os.path.join(out_dir, f"{base_name}.json")
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
                print(f"✓ Converted: {xml_file} -> {out_file}")
            except Exception as e:
                print(f"✗ Failed to convert {xml_file}: {e}", file=sys.stderr)

        print(f"\nSuccessfully processed {len(xml_files)} files into {out_dir}")
        return 0

    elif os.path.isfile(input_path):
        try:
            data = parse_ccda_file(input_path, strict=args.strict)

            if filter_sections:
                data["sections"] = {k: v for k, v in data["sections"].items() if k.lower() in filter_sections}

            if args.summary:
                print_summary(data)

            if args.csv_export:
                export_to_csv(data, args.csv_export)
                print(f"✓ Exported CSV tables to {args.csv_export}")

            json_str = json.dumps(data, indent=indent, ensure_ascii=False, default=str)

            if args.output:
                os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(json_str)
                print(f"✓ JSON saved to {args.output}")
            elif not args.summary:
                print(json_str)

            return 0

        except Exception as e:
            print(f"Error parsing C-CDA document: {e}", file=sys.stderr)
            return 1
    else:
        print(f"File or directory not found: {input_path}", file=sys.stderr)
        return 1


def print_summary(data: Dict[str, Any]) -> None:
    """Print high-level clinical summary of the document."""
    meta = data.get("document_meta", {})
    patient = data.get("patient", {})
    summary = data.get("summary", {})

    print("\n" + "=" * 60)
    print(f" CLINICAL DOCUMENT SUMMARY: {meta.get('title', 'Clinical Document')}")
    print("=" * 60)
    print(f" Patient Name : {summary.get('patient_name', 'Unknown')}")
    print(f" Date of Birth: {summary.get('date_of_birth', 'Unknown')}")
    print(f" Gender       : {summary.get('gender', 'Unknown')}")
    print(f" Document Date: {meta.get('effective_time', 'Unknown')}")
    print("-" * 60)
    print(" Clinical Data Counts:")
    counts = summary.get("counts", {})
    for k, v in counts.items():
        print(f"   • {k.replace('_', ' ').capitalize():<18}: {v}")
    print("-" * 60)
    print(f" Available Sections: {', '.join(summary.get('available_sections', []))}")
    print("=" * 60 + "\n")


def export_to_csv(data: Dict[str, Any], output_dir: str) -> None:
    """Export clinical entries from sections into CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    sections = data.get("sections", {})

    # Allergies CSV
    allergies = sections.get("allergies", {}).get("entries", [])
    if allergies:
        with open(os.path.join(output_dir, "allergies.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Substance", "Code", "CodeSystem", "Status", "Severity", "Reactions"])
            for a in allergies:
                sub = a.get("substance") or {}
                sub_name = sub.get("display_name") or sub.get("original_text", "")
                sub_code = sub.get("code", "")
                sub_sys = sub.get("code_system_name", "")
                stat = a.get("status", "")
                sev = a.get("severity", {})
                sev_str = sev.get("display_name") if isinstance(sev, dict) else str(sev or "")
                rx_list = []
                for rx in a.get("reactions", []):
                    r_val = rx.get("reaction") or {}
                    rx_name = r_val.get("display_name") if isinstance(r_val, dict) else str(r_val)
                    if rx_name:
                        rx_list.append(rx_name)
                writer.writerow([sub_name, sub_code, sub_sys, stat, sev_str, "; ".join(rx_list)])

    # Medications CSV
    medications = sections.get("medications", {}).get("entries", [])
    if medications:
        with open(os.path.join(output_dir, "medications.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Medication", "Code", "CodeSystem", "Status", "Dose", "Route", "Schedule", "Start Date", "End Date"])
            for m in medications:
                med = m.get("medication") or {}
                med_name = med.get("display_name") or med.get("original_text", "")
                med_code = med.get("code", "")
                med_sys = med.get("code_system_name", "")
                stat = m.get("status", "")
                dose = (m.get("dose") or {}).get("formatted", "")
                route = (m.get("route") or {}).get("display_name", "")
                sched = (m.get("schedule") or {}).get("period", {}).get("human_readable", "")
                dr = m.get("date_range") or {}
                start_date = dr.get("low", "")
                end_date = dr.get("high", "")
                writer.writerow([med_name, med_code, med_sys, stat, dose, route, sched, start_date, end_date])

    # Problems CSV
    problems = sections.get("problems", {}).get("entries", [])
    if problems:
        with open(os.path.join(output_dir, "problems.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Condition/Problem", "Code", "CodeSystem", "Status", "Onset Date", "Age At Onset"])
            for p in problems:
                prob = p.get("problem") or {}
                p_name = prob.get("display_name") or prob.get("original_text", "")
                p_code = prob.get("code", "")
                p_sys = prob.get("code_system_name", "")
                stat = p.get("status", "")
                eff_time = p.get("effective_time")
                onset = eff_time.get("low") if isinstance(eff_time, dict) else str(eff_time or "")
                age = (p.get("age_at_onset") or {}).get("formatted", "")
                writer.writerow([p_name, p_code, p_sys, stat, onset, age])

    # Vital Signs CSV
    vitals = sections.get("vital_signs", {}).get("measurements", [])
    if vitals:
        with open(os.path.join(output_dir, "vital_signs.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Vital Sign", "Code", "Value", "Unit", "Interpretation", "Date"])
            for v in vitals:
                vital_code = v.get("vital_sign") or {}
                name = vital_code.get("display_name", "")
                code = vital_code.get("code", "")
                val_dict = v.get("value") or {}
                val = val_dict.get("value", "")
                unit = val_dict.get("unit", "")
                interp = (v.get("interpretation") or {}).get("display_name", "")
                date = v.get("date", "")
                writer.writerow([name, code, val, unit, interp, date])

    # Results CSV
    results = sections.get("results", {}).get("results", [])
    if results:
        with open(os.path.join(output_dir, "lab_results.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Test Name", "LOINC Code", "Result Value", "Unit", "Interpretation", "Reference Range", "Date"])
            for r in results:
                test = r.get("test") or {}
                name = test.get("display_name", "")
                code = test.get("code", "")
                val_dict = r.get("value") or {}
                val = val_dict.get("value", "")
                unit = val_dict.get("unit", "")
                interp = (r.get("interpretation") or {}).get("display_name", "")
                ref_range = r.get("reference_range", "")
                date = r.get("date", "")
                writer.writerow([name, code, val, unit, interp, ref_range, date])


if __name__ == "__main__":
    sys.exit(main())
