#!/bin/bash
set -e

echo ">>> STARTING ALL TESTS <<<"

echo "1. Running Unit Tests (pytest)..."
pytest
echo "✅ Unit Tests Passed"

echo "2. Running Comprehensive System Test..."
python3 test_comprehensive.py
echo "✅ Comprehensive Test Passed"

echo "Running New Feature Tests..."
python3 test_new_features.py

echo "Running Shared View Tests..."
pytest test_shared_view.py
echo "✅ New Features Test Passed"

echo ">>> ALL TESTS PASSED SUCCESSFULLY <<<"
