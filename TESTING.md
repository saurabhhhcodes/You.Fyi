# You.fyi Testing Guide

Complete guide for testing the You.fyi API with pytest and real LLM integration.

## Quick Start

### 1. Setup

```bash
cd /home/saurabh/You.Fyi
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
# OR create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### 3. Run Tests

```bash
# All tests (API tests run, LLM tests skip if no key)
pytest tests/ -v

# Only API tests (no LLM)
pytest tests/test_api.py -v

# Only LLM tests (requires API key)
pytest tests/test_rag.py -v

# With coverage report
pytest tests/ --cov=app --cov-report=html
```

## Test Files

### `tests/test_api.py` - Core API Tests
Tests all CRUD operations without external dependencies.

**Test Classes:**
- `TestWorkspaces` - Workspace management
- `TestAssets` - Asset creation and retrieval
- `TestKits` - Kit management with assets
- `TestSharingLinks` - Sharing link creation and management

**Key Tests:**
```python
# Create workspace
test_create_workspace()

# Manage assets
test_create_asset()
test_list_assets()

# Kit operations
test_create_kit_with_assets()
test_update_kit()

# Sharing links
test_create_sharing_link()
test_deactivate_sharing_link()
```

### `tests/test_rag.py` - RAG & LLM Tests
Tests with real OpenAI API calls.

**Test Classes:**
- `TestLLMService` - Raw LLM functionality
- `TestRAGService` - RAG service methods
- `TestRAGEndpoints` - RAG API endpoints

**Key Tests:**
```python
# Real LLM calls (require API key)
TestLLMService::test_query_with_context()
TestLLMService::test_summarize_assets()
TestLLMService::test_semantic_search()

# RAG pipeline
TestRAGService::test_retrieve_and_answer()

# API endpoints
TestRAGEndpoints::test_query_rag_with_assets_real_llm()
TestRAGEndpoints::test_query_rag_via_sharing_link()
```

### `tests/test_file_uploads.py` - File Upload Tests
Comprehensive tests for file upload functionality with support for all file types.

**Test Classes:**
- `TestImageUpload` - Image file uploads (PNG, JPG, GIF, etc.)
- `TestVideoUpload` - Video file uploads (MP4, WebM, etc.)
- `TestDocumentUpload` - Document uploads (PDF, TXT, CSV)
- `TestExecutableUpload` - Executable and script files (EXE, PY, etc.)
- `TestArchiveUpload` - Archive uploads (ZIP, TAR.GZ, etc.)
- `TestFileOperations` - Upload, download, list operations
- `TestErrorHandling` - Error scenarios
- `TestLargeFiles` - Large file handling (1MB+)
- `TestMimeTypeDetection` - MIME type classification
- `TestFileIntegration` - Integration with other features

**Key Tests:**
```python
# Upload tests
TestImageUpload::test_upload_png_image()
TestVideoUpload::test_upload_mp4_video()
TestDocumentUpload::test_upload_pdf_document()
TestExecutableUpload::test_upload_exe_executable()
TestArchiveUpload::test_upload_zip_archive()

# Operations
TestFileOperations::test_upload_and_list_files()
TestFileOperations::test_download_uploaded_file()
TestFileOperations::test_get_file_metadata()

# Integration
TestFileIntegration::test_upload_and_add_to_kit()
TestFileIntegration::test_multiple_file_uploads_different_types()

# Error handling
TestErrorHandling::test_upload_to_nonexistent_workspace()
TestErrorHandling::test_download_nonexistent_file()
TestErrorHandling::test_upload_without_file()

# Performance
TestLargeFiles::test_upload_large_binary_file()
```

**22 File Upload Tests - All Passing ✅**

## Testing Scenarios

### Scenario 1: Test Without LLM (Fast, No API)

**Run:**
```bash
pytest tests/test_api.py tests/test_file_uploads.py -v
```

**What's Tested:**
- ✓ All CRUD operations
- ✓ Data persistence
- ✓ Relationships (kits with assets)
- ✓ Sharing link generation
- ✓ API validation

**Time:** ~5-10 seconds

### Scenario 2: Test With Real LLM (Full Integration)

**Setup:**
```bash
export OPENAI_API_KEY="sk-your-key"
```

**Run:**
```bash
pytest tests/test_rag.py::TestLLMService -v
```

**What's Tested:**
- ✓ OpenAI API connectivity
- ✓ Query with context generation
- ✓ Document summarization
- ✓ Semantic search
- ✓ Full RAG pipeline

**Time:** ~30-60 seconds (depends on API response)

### Scenario 3: Test RAG Query Endpoint

**Setup:**
```bash
export OPENAI_API_KEY="sk-your-key"
```

**Run:**
```bash
pytest tests/test_rag.py::TestRAGEndpoints::test_query_rag_with_assets_real_llm -v
```

**What's Tested:**
- ✓ Query endpoint validation
- ✓ Kit and asset retrieval
- ✓ LLM integration
- ✓ Response formatting

### Scenario 4: Test Sharing Links

**Run:**
```bash
pytest tests/test_rag.py::TestRAGEndpoints::test_query_rag_via_sharing_link -v
```

**What's Tested:**
- ✓ Sharing link creation
- ✓ Token-based access
- ✓ RAG queries via sharing link

### Scenario 5: Test File Uploads (Images, Videos, Documents, etc.)

**Run:**
```bash
pytest tests/test_file_uploads.py -v
```

**What's Tested:**
- ✓ Image uploads (PNG, JPG, GIF)
- ✓ Video uploads (MP4, WebM)
- ✓ Document uploads (PDF, TXT, CSV)
- ✓ Executable uploads (EXE, PY, etc.)
- ✓ Archive uploads (ZIP, TAR.GZ)
- ✓ File download functionality
- ✓ Metadata retrieval
- ✓ Large file handling (1MB+)
- ✓ MIME type detection
- ✓ Error handling

**Time:** ~3-5 seconds

**Example Output:**
```
tests/test_file_uploads.py::TestImageUpload::test_upload_png_image PASSED
tests/test_file_uploads.py::TestImageUpload::test_upload_jpg_image PASSED
tests/test_file_uploads.py::TestVideoUpload::test_upload_mp4_video PASSED
tests/test_file_uploads.py::TestDocumentUpload::test_upload_pdf_document PASSED
tests/test_file_uploads.py::TestExecutableUpload::test_upload_exe_executable PASSED
tests/test_file_uploads.py::TestArchiveUpload::test_upload_zip_archive PASSED
tests/test_file_uploads.py::TestFileOperations::test_upload_and_list_files PASSED
tests/test_file_uploads.py::TestFileOperations::test_download_uploaded_file PASSED
tests/test_file_uploads.py::TestFileIntegration::test_upload_and_add_to_kit PASSED
======================== 22 passed in 2.57s ========================
```

## Running Specific Tests

### By Class
```bash
pytest tests/test_api.py::TestWorkspaces -v
pytest tests/test_api.py::TestAssets -v
pytest tests/test_file_uploads.py::TestImageUpload -v
pytest tests/test_file_uploads.py::TestFileOperations -v
pytest tests/test_rag.py::TestLLMService -v
```

### By Method
```bash
pytest tests/test_api.py::TestWorkspaces::test_create_workspace -v
pytest tests/test_file_uploads.py::TestFileOperations::test_download_uploaded_file -v
pytest tests/test_rag.py::TestLLMService::test_query_with_context -v
```

### By Pattern
```bash
pytest tests/ -k "workspace" -v
pytest tests/ -k "asset" -v
pytest tests/ -k "upload" -v
pytest tests/ -k "file" -v
pytest tests/ -k "rag" -v
```

### With Markers
```bash
pytest tests/ -m "slow" -v
pytest tests/ -m "integration" -v
```

## Coverage Reports

### Generate HTML Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

**View Report:**
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage by Module

```bash
pytest tests/ --cov=app.models --cov-report=term
pytest tests/ --cov=app.services --cov-report=term
pytest tests/ --cov=app.routes --cov-report=term
```

## Testing with Different Configurations

### Minimal Test (No Dependencies)

```bash
pytest tests/test_api.py::TestWorkspaces::test_create_workspace -v
```

### Full Test Suite

```bash
pytest tests/ -v --tb=short
```

### Verbose Output

```bash
pytest tests/ -vv --tb=long
```

### Show Print Statements

```bash
pytest tests/ -v -s
```

## Environment Setup for Testing

### Create Test Environment

```bash
# Option 1: Using bash script
chmod +x setup.sh
./setup.sh

# Option 2: Manual setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Verify Setup

```bash
python -c "
from app.main import app
from app.services import LLMService
from app.models import Workspace, Asset, Kit, SharingLink
print('✓ All imports successful')
"
```

### Test Database Setup

## Manual File Upload Testing (cURL)

### Setup

```bash
# 1. Start the server
uvicorn app.main:app --reload &

# 2. In another terminal, create a workspace
WORKSPACE=$(curl -X POST http://localhost:8000/workspaces/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "description": "Test workspace"}' | jq -r '.id')

echo "Workspace ID: $WORKSPACE"
```

### Test Image Upload

```bash
# Create a test image
python3 << 'EOF'
from PIL import Image
img = Image.new('RGB', (100, 100), color='red')
img.save('test_image.png')
EOF

# Upload
curl -X POST http://localhost:8000/assets/${WORKSPACE}/upload \
  -F "file=@test_image.png" \
  -F "description=Test image"
```

### Test PDF Upload

```bash
# Create a simple PDF
python3 << 'EOF'
from reportlab.pdfgen import canvas
c = canvas.Canvas("test.pdf")
c.drawString(100, 750, "Test PDF Content")
c.save()
EOF

# Upload
curl -X POST http://localhost:8000/assets/${WORKSPACE}/upload \
  -F "file=@test.pdf" \
  -F "description=Test PDF"
```

### Test Video Upload

```bash
# Create test video (using ffmpeg)
ffmpeg -f lavfi -i testsrc=s=320x240:d=1 -f lavfi -i sine=f=440:d=1 test.mp4

# Upload
curl -X POST http://localhost:8000/assets/${WORKSPACE}/upload \
  -F "file=@test.mp4" \
  -F "description=Test video"
```

### Test Executable Upload

```bash
# Create a simple executable (example)
echo '#!/bin/bash
echo "Hello from test script"' > test_script.sh
chmod +x test_script.sh

# Upload
curl -X POST http://localhost:8000/assets/${WORKSPACE}/upload \
  -F "file=@test_script.sh" \
  -F "description=Test script"
```

### List Files

```bash
curl -X GET http://localhost:8000/assets/${WORKSPACE} | jq '.'
```

### Download File

```bash
ASSET_ID=$(curl -X GET http://localhost:8000/assets/${WORKSPACE} | jq -r '.[0].id')

curl -X GET http://localhost:8000/assets/asset/${ASSET_ID}/download \
  -o downloaded_file
```

### Get File Metadata

```bash
curl -X GET http://localhost:8000/assets/asset/${ASSET_ID} | jq '.'
```

## Troubleshooting Tests

### Issue: Import Errors

**Solution:**
```bash
cd /home/saurabh/You.Fyi
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: OPENAI_API_KEY Not Found

**Solution:**
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set key
export OPENAI_API_KEY="sk-your-key"

# Or use .env
echo "OPENAI_API_KEY=sk-your-key" > .env
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Issue: Database Errors

**Solution:**
```bash
# Clean up test databases
rm test.db test_rag.db youfyi.db

# Re-run tests (recreate automatically)
pytest tests/ -v
```

### Issue: Rate Limiting (LLM Tests)

**Solution:**
```bash
# Add delay between tests
pytest tests/test_rag.py -v --durations=10

# Run fewer tests
pytest tests/test_rag.py::TestLLMService::test_query_with_context -v
```

## Real LLM Testing Details

### What Happens During LLM Test

1. **Query with Context**
   ```
   Context: "Python is a programming language..."
   Question: "What is Python?"
   → OpenAI generates answer based on context
   ```

2. **Semantic Search**
   ```
   Query: "What is Python?"
   Documents: [doc1, doc2, doc3]
   → OpenAI returns most relevant document indices
   ```

3. **Summarization**
   ```
   Assets: [content1, content2, content3]
   → OpenAI generates summary of all content
   ```

### Cost Estimation

- Small test (~20 requests): ~$0.001-0.01
- Full suite (if all LLM tests): ~$0.05-0.10
- Token limit: typically 4K tokens per request

### Optimization for LLM Tests

```bash
# Run only quick tests
pytest tests/test_rag.py::TestLLMService::test_query_with_context -v

# Run tests without expensive operations
pytest tests/test_rag.py::TestRAGEndpoints -k "no_llm" -v
```

## Continuous Integration Setup

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/test_api.py -v
      - run: pytest tests/test_rag.py -v
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Best Practices

1. **Isolate Tests** - Each test creates/cleans up own data
2. **Use Fixtures** - Reuse setup code with pytest fixtures
3. **Test Real Scenarios** - Test actual LLM calls occasionally
4. **Mock External APIs** - Use mocking for CI/CD to save costs
5. **Check Coverage** - Aim for >80% code coverage
6. **Test Edge Cases** - Empty kits, expired links, missing assets

## Sample Test Run Output

```
tests/test_api.py::TestWorkspaces::test_create_workspace PASSED    [ 2%]
tests/test_api.py::TestWorkspaces::test_list_workspaces PASSED     [ 4%]
tests/test_api.py::TestWorkspaces::test_get_workspace PASSED       [ 6%]
tests/test_api.py::TestAssets::test_create_asset PASSED            [ 8%]
tests/test_api.py::TestKits::test_create_kit_with_assets PASSED    [10%]
tests/test_api.py::TestSharingLinks::test_create_sharing_link PASSED [12%]

tests/test_rag.py::TestLLMService::test_query_with_context PASSED  [50%]
tests/test_rag.py::TestRAGEndpoints::test_query_rag_with_assets_real_llm PASSED [70%]

====== 15 passed in 2.45s ======
```

## Next Steps

1. Run `pytest tests/test_api.py -v` to verify all API tests pass
2. Set your OpenAI API key: `export OPENAI_API_KEY="sk-..."`
3. Run `pytest tests/test_rag.py -v` to test real LLM integration
4. Generate coverage: `pytest tests/ --cov=app --cov-report=html`
5. Review test files for examples and patterns

## Support

For issues:
- Check test output with `-v -s` flags
- Review test fixtures in test files
- Verify OPENAI_API_KEY is set for LLM tests
- Check database connectivity for API tests
