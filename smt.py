#!/usr/bin/env python3
"""
SMT (ScrumMaster Tools) - Short entry point
Author: Marek Mróz <marek@mroz.consulting>

Quick access to ScrumMaster Tools with shorter name.
Usage: python smt.py
"""
import sys
import os
import warnings

# Suppress urllib3 LibreSSL warnings on macOS
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

# Add path to src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrummaster.cli import main

if __name__ == "__main__":
    main()