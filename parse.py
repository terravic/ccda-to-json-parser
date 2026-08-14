#!/usr/bin/env python3
"""
Root-level quick runner for C-CDA to JSON Parser.
Usage:
    python3 parse.py samples/sample_1_continuity_of_care_document.xml
    python3 parse.py samples/sample_1_continuity_of_care_document.xml -o output.json
    python3 parse.py samples/sample_1_continuity_of_care_document.xml --summary
"""

import os
import sys

# Ensure src directory is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from ccda_parser.cli import main

if __name__ == "__main__":
    sys.exit(main())
