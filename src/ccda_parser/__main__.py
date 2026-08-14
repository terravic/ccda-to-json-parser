"""
Module execution entry point: python3 -m ccda_parser
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
