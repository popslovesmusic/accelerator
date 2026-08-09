#!/usr/bin/env python3
import sys
import os

# Adjust path to find sibling python modules in same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    main()
