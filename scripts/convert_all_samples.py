#!/usr/bin/env python3
"""
Batch converter script for sample C-CDA files.
Demonstrates end-to-end conversion and outputs pretty JSON files.
"""

import json
import os
import sys

# Ensure src is in Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from ccda_parser import generate_patient_dashboard_html, parse_ccda_file
from ccda_parser.cli import print_summary


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_dir = os.path.join(base_dir, "samples")
    output_dir = os.path.join(samples_dir, "converted_json")
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    sample_files = [
        f for f in os.listdir(samples_dir)
        if f.endswith(".xml")
    ]

    print("=" * 70)
    print(" C-CDA TO JSON PARSER - BATCH SAMPLE CONVERTER & DASHBOARDS")
    print("=" * 70)

    for sf in sorted(sample_files):
        xml_path = os.path.join(samples_dir, sf)
        base_name = os.path.splitext(sf)[0]
        json_path = os.path.join(output_dir, f"{base_name}.json")

        print(f"\nProcessing: {sf} ...")
        try:
            with open(xml_path, "r", encoding="utf-8", errors="replace") as xf:
                raw_xml = xf.read()

            parsed_data = parse_ccda_file(xml_path)
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False, default=str)

            rel_json_path = os.path.relpath(json_path, base_dir)
            print(f"✓ Successfully generated JSON: {rel_json_path}")

            # Generate dashboard for sample 1
            if "sample_1" in sf:
                dash_path = os.path.join(docs_dir, "sample_1_patient_dashboard.html")
                dash_html = generate_patient_dashboard_html(parsed_data, raw_input=raw_xml, input_filename=sf)
                with open(dash_path, "w", encoding="utf-8") as df:
                    df.write(dash_html)
                print(f"✓ Successfully generated Dashboard: {os.path.relpath(dash_path, base_dir)}")

            print_summary(parsed_data)

        except Exception as e:
            print(f"✗ Failed to convert {sf}: {e}", file=sys.stderr)

    rel_output_dir = os.path.relpath(output_dir, base_dir)
    print("\nAll samples converted successfully!")
    print(f"JSON outputs saved in: {rel_output_dir}")


if __name__ == "__main__":
    main()
