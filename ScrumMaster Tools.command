#!/bin/bash

# Navigate to script directory
cd "$(dirname "$0")"

# Clear screen
clear

# Display startup information
echo "========================================="
echo "   ScrumMaster Tools 2.11.1 (SMT)"
echo "========================================="
echo ""

# Activate virtual environment
source venv/bin/activate

# Run main script
python3 smt.py

# Deactivate virtual environment
deactivate 2>/dev/null || true

# Keep terminal window open
echo ""
echo "========================================="
echo "Program finished."
echo ""
echo "Press Enter to close terminal..."
read

# Close terminal window
osascript -e 'tell application "Terminal" to close front window' &>/dev/null