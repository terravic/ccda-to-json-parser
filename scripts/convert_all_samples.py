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

from ccda_parser import parse_ccda_file
from ccda_parser.cli import print_summary


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_dir = os.path.join(base_dir, "samples")
    output_dir = os.path.join(samples_dir, "converted_json")
    os.makedirs(output_dir, exist_ok=True)

    sample_files = [
        f for f in os.listdir(samples_dir)
        if f.endswith(".xml")
    ]

    print("=" * 70)
    print(" C-CDA TO JSON PARSER - BATCH SAMPLE CONVERTER")
    print("=" * 70)

    for sf in sorted(sample_files):
        xml_path = os.path.join(samples_dir, sf)
        base_name = os.path.splitext(sf)[0]
        json_path = os.path.join(output_dir, f"{base_name}.json")

        print(f"\nProcessing: {sf} ...")
        try:
            parsed_data = parse_ccda_file(xml_path)
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False, default=str)

            print(f"✓ Successfully generated: {json_path}")
            print_summary(parsed_data)

        except Exception as e:
            print(f"✗ Failed to convert {sf}: {e}", file=sys.stderr)

    print("\nAll samples converted successfully!")
    print(f"JSON outputs saved in: {output_dir}")


if __name__ == "__main__":
    main()
