#!/usr/bin/env python3
"""
Module-level entry point for the Alpaca Market Data Explorer.
Allows running the data explorer using: python -m alpaca_trader.official.data
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_explorer import main

if __name__ == "__main__":
    main() 