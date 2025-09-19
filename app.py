#!/usr/bin/env python3
"""
Streamlit app entry point for cloud deployment
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import and run the dashboard
from src.reporting.dashboard import run_dashboard

if __name__ == "__main__":
    run_dashboard()
