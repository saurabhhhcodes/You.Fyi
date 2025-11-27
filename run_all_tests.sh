#!/bin/bash
set -e

echo ">>> STARTING ALL TESTS <<<"

echo "1. Running Unit Tests (pytest)..."
pytest
echo "✅ Unit Tests Passed"

echo "2. Running Comprehensive System Test..."
python3 test_comprehensive.py
echo "✅ Comprehensive Test Passed"

echo "3. Running New Features Test..."
python3 test_new_features.py
echo "✅ New Features Test Passed"

echo ">>> ALL TESTS PASSED SUCCESSFULLY <<<"
