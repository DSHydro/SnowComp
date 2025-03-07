#!/usr/bin/env python
"""
Convenience script for running the Skagit Snow Analysis tool.
This allows the package to be run without installation using:
python -m skagit_snow_analysis.run
"""

from .cli import main

if __name__ == "__main__":
    main()