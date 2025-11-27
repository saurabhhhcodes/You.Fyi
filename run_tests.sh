#!/bin/bash
echo "Running comprehensive API tests..."
# Ensure dependencies are installed
pip install -r requirements.txt > /dev/null 2>&1

# Run the test script
python3 test_comprehensive.py
