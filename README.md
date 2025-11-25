# You.fyi - Smart Workspace with RAG

A modern API-first platform for managing workspaces, assets, kits, and retrieval-augmented generation (RAG) with OpenAI LLM integration.

## Features

✅ **Workspace Management** - Create and manage isolated workspaces
✅ **Assets** - Store and organize documents, data, and content
✅ **File Uploads** - Upload images, videos, documents, executables, and more
✅ **Kits** - Group related assets together
✅ **Sharing Links** - Create shareable, time-limited access links to kits
✅ **RAG with LLM** - Query your assets using OpenAI's GPT models
✅ **Semantic Search** - Intelligent document retrieval using LLM
✅ **Smart Contract Ready** - Backend architecture prepared for blockchain integration

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLAlchemy ORM (SQLite for development)
- **Testing**: pytest
- **LLM**: OpenAI API (gpt-3.5-turbo)
- **API Documentation**: Swagger/OpenAPI

## Quick Start

### 1. Clone and Setup

```bash
cd /home/saurabh/You.Fyi
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_api.py -v
pytest tests/test_rag.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html to view coverage report
```

### Run Only LLM Tests (requires OPENAI_API_KEY)

```bash
pytest tests/test_rag.py::TestLLMService -v
pytest tests/test_rag.py::TestRAGEndpoints::test_query_rag_with_assets_real_llm -v
```

### Run Tests Without LLM (skips API calls)

```bash
pytest tests/test_api.py -v
pytest tests/test_rag.py::TestRAGEndpoints::test_query_rag_with_assets_no_llm -v
```

## API Endpoints

### Workspaces
- `POST /workspaces/` - Create workspace
- `GET /workspaces/` - List all workspaces
- `GET /workspaces/{workspace_id}` - Get workspace
- `DELETE /workspaces/{workspace_id}` - Delete workspace

### Assets
- `POST /assets/{workspace_id}` - Create asset (text/json content)
- `POST /assets/{workspace_id}/upload` - Upload file (images, videos, documents, executables, archives)
- `GET /assets/{workspace_id}` - List assets in workspace
- `GET /assets/asset/{asset_id}` - Get specific asset
- `GET /assets/asset/{asset_id}/download` - Download file
- `DELETE /assets/asset/{asset_id}` - Delete asset

### Kits
- `POST /kits/{workspace_id}` - Create kit
- `GET /kits/{workspace_id}` - List kits in workspace
- `GET /kits/kit/{kit_id}` - Get specific kit
- `PUT /kits/kit/{kit_id}` - Update kit
- `DELETE /kits/kit/{kit_id}` - Delete kit

### Sharing Links
- `POST /sharing-links/kit/{kit_id}` - Create sharing link
- `GET /sharing-links/token/{token}` - Get link by token
- `GET /sharing-links/kit/{kit_id}` - List links for kit
- `DELETE /sharing-links/{link_id}` - Delete link
- `PATCH /sharing-links/{link_id}/deactivate` - Deactivate link

### RAG (Retrieval-Augmented Generation)
- `POST /rag/query` - Query kit with LLM
- `POST /rag/query/shared/{token}` - Query via sharing link

## Example Usage

### 1. Create a Workspace

```bash
curl -X POST http://localhost:8000/workspaces/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Project documentation"
  }'
```

Response:
```json
{
  "id": "uuid-here",
  "name": "My Project",
  "description": "Project documentation",
  "created_at": "2025-11-20T10:00:00",
  "updated_at": "2025-11-20T10:00:00"
}
```

### 2. Create Assets

```bash
curl -X POST http://localhost:8000/assets/{workspace_id} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Documentation",
    "description": "REST API docs",
    "content": "This is detailed API documentation...",
    "asset_type": "document"
  }'
```

### 4. Upload Files

Upload various file types to workspace:

```bash
# Upload an image
curl -X POST http://localhost:8000/assets/{workspace_id}/upload \
  -F "file=@image.png" \
  -F "description=Product screenshot"

# Upload a video
curl -X POST http://localhost:8000/assets/{workspace_id}/upload \
  -F "file=@tutorial.mp4" \
  -F "description=How-to video"

# Upload a document
curl -X POST http://localhost:8000/assets/{workspace_id}/upload \
  -F "file=@report.pdf" \
  -F "description=Q1 Report"

# Upload an executable
curl -X POST http://localhost:8000/assets/{workspace_id}/upload \
  -F "file=@installer.exe" \
  -F "description=Application installer"

# Upload a code file
curl -X POST http://localhost:8000/assets/{workspace_id}/upload \
  -F "file=@script.py" \
  -F "description=Python automation script"

# Upload an archive
curl -X POST http://localhost:8000/assets/{workspace_id}/upload \
  -F "file=@project.zip" \
  -F "description=Source code"
```

Response:
```json
{
  "id": "asset-id",
  "workspace_id": "workspace-id",
  "name": "image.png",
  "description": "Product screenshot",
  "content": "base64-encoded-file-content",
  "asset_type": "image",
  "mime_type": "image/png",
  "file_size": 156234,
  "file_path": "image.png",
  "created_at": "2025-11-20T10:00:00",
  "updated_at": "2025-11-20T10:00:00"
}
```

**Supported File Types**:
- **Images**: PNG, JPG, GIF, WebP, SVG, BMP (MIME: `image/*`)
- **Videos**: MP4, AVI, MOV, MKV, WebM, FLV, WMV (MIME: `video/*`)
- **Audio**: MP3, WAV, OGG, FLAC (MIME: `audio/*`)
- **Documents**: PDF, DOCX, XLSX, PPTX, TXT, CSV (MIME: `application/pdf`, `application/vnd.*`, `text/*`)
- **Code/Executables**: EXE, PY, JS, JAVA, C++, SH, BAT (MIME: `text/x-python`, `application/x-msdownload`)
- **Archives**: ZIP, RAR, TAR, GZ, 7Z (MIME: `application/zip`, `application/gzip`)
- **Any other file type**: Automatically classified as generic file

### 5. Download Files

```bash
# Get file metadata
curl -X GET http://localhost:8000/assets/asset/{asset_id}

# Download file
curl -X GET http://localhost:8000/assets/asset/{asset_id}/download \
  -o downloaded_file.ext
```

### 6. Create a Kit

```bash
curl -X POST http://localhost:8000/kits/{workspace_id} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Documentation Kit",
    "description": "All documentation assets",
    "asset_ids": ["asset-id-1", "asset-id-2"]
  }'
```

### 7. Create Sharing Link

```bash
curl -X POST http://localhost:8000/sharing-links/kit/{kit_id} \
  -H "Content-Type: application/json" \
  -d '{
    "expires_in_days": 7
  }'
```

Response:
```json
{
  "id": "link-id",
  "kit_id": "kit-id",
  "token": "secure-token-here",
  "is_active": true,
  "created_at": "2025-11-20T10:00:00",
  "expires_at": "2025-11-27T10:00:00"
}
```

### 8. Query with RAG (Real LLM)

```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is in the files?",
    "kit_id": "kit-id",
    "use_llm": true
  }'
```

Response:
```json
{
  "query": "What is in the files?",
  "answer": "Based on the uploaded files, the content includes...",
  "sources": ["asset-id-1", "asset-id-2"],
  "model": "gpt-3.5-turbo"
}
```

### 9. Query via Sharing Link

```bash
curl -X POST http://localhost:8000/rag/query/shared/{token} \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What information is available?",
    "use_llm": true
  }'
```

## Testing Strategy

### Unit Tests
- Located in `tests/test_api.py` (19 tests)
- Tests all CRUD operations for workspaces, assets, kits, and sharing links
- No external dependencies required

### File Upload Tests
- Located in `tests/test_file_uploads.py` (22 tests)
- Tests uploading all supported file types
- Tests download, metadata retrieval, and error handling
- Tests MIME type detection and asset type classification
- Tests large file uploads (1MB+)

### Integration Tests with Real LLM
- Located in `tests/test_rag.py`
- Tests real OpenAI API calls
### 4. Create Sharing Link

```bash
curl -X POST http://localhost:8000/sharing-links/kit/{kit_id} \
  -H "Content-Type: application/json" \
  -d '{
    "expires_in_days": 7
  }'
```

Response:
```json
{
  "id": "link-id",
  "kit_id": "kit-id",
  "token": "secure-token-here",
  "is_active": true,
  "created_at": "2025-11-20T10:00:00",
  "expires_at": "2025-11-27T10:00:00"
}
```

### 5. Query with RAG (Real LLM)

```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "kit_id": "kit-id",
    "use_llm": true
  }'
```

Response:
```json
{
  "query": "What is the main topic?",
  "answer": "Based on the documentation, the main topic is...",
  "sources": ["asset-id-1", "asset-id-2"],
  "model": "gpt-3.5-turbo"
}
```

### 6. Query via Sharing Link

```bash
curl -X POST http://localhost:8000/rag/query/shared/{token} \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is in the documentation?",
    "use_llm": true
  }'
```

## Testing Strategy

### Unit Tests
- Located in `tests/test_api.py`
- Tests all CRUD operations for workspaces, assets, kits, and sharing links
- No external dependencies required

### Integration Tests with Real LLM
- Located in `tests/test_rag.py`
- Tests real OpenAI API calls
- Requires `OPENAI_API_KEY` environment variable
- Tests are automatically skipped if API key is not provided
- Tests:
  - `test_query_with_context()` - Real context-based queries
  - `test_summarize_assets()` - Asset summarization
  - `test_semantic_search()` - Smart document retrieval
  - `test_query_rag_with_assets_real_llm()` - Full RAG pipeline

### Running Tests Step-by-Step

1. **Setup Phase**
   ```bash
   source venv/bin/activate
   export OPENAI_API_KEY="sk-your-key"
   ```

2. **Run API Tests (No LLM)**
   ```bash
   pytest tests/test_api.py -v
   # Should pass without OpenAI API key
   ```

3. **Run LLM Tests (With Real API)**
   ```bash
   pytest tests/test_rag.py -v
   # Skips if OPENAI_API_KEY not set, runs real LLM tests if available
   ```

4. **Run All Tests**
   ```bash
   pytest tests/ -v --tb=short
   ```

5. **View Coverage**
   ```bash
   pytest tests/ --cov=app --cov-report=html
   open htmlcov/index.html
   ```

## Project Structure

```
You.Fyi/
├── app/
│   ├── models/              # Database models
│   │   └── __init__.py     # Workspace, Asset, Kit, SharingLink
│   ├── routes/              # API endpoints
│   │   ├── workspaces.py
│   │   ├── assets.py
│   │   ├── kits.py
│   │   ├── sharing_links.py
│   │   └── rag.py
│   ├── services/            # Business logic
│   │   ├── __init__.py     # LLMService with real OpenAI calls
│   │   └── rag.py          # RAGService
│   ├── schemas/             # Pydantic models
│   │   └── __init__.py
│   ├── database.py          # Database configuration
│   └── main.py              # FastAPI app
├── tests/
│   ├── test_api.py          # API tests (no LLM)
│   └── test_rag.py          # RAG tests (with real LLM)
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

## LLM Integration Details

### Real OpenAI API Calls

The `LLMService` class in `app/services/__init__.py` makes real API calls to OpenAI:

```python
# Real API calls happen here
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[...],
    temperature=0.7,
    max_tokens=500,
)
```

### Implemented LLM Functions

1. **Query with Context** - Answer questions based on provided document content
2. **Summarize Assets** - Create summaries of multiple documents
3. **Semantic Search** - Find most relevant documents for a query

### RAG Pipeline

```
User Query
    ↓
Semantic Search (LLM) → Find relevant assets
    ↓
Context Assembly → Combine relevant documents
    ↓
Query with Context (LLM) → Generate answer
    ↓
Response with Sources
```

## Environment Variables

Create a `.env` file:

```
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=sqlite:///./youfyi.db
DEBUG=True
```

## Future Enhancements

- [ ] Smart contract integration for ownership verification
- [ ] Advanced semantic search with embeddings
- [ ] User authentication and authorization
- [ ] Real-time collaboration
- [ ] WebSocket support for live updates
- [ ] PostgreSQL support for production
- [ ] Docker containerization
- [ ] CI/CD pipeline with GitHub Actions

## Troubleshooting

### OpenAI API Key Issues
```bash
# Verify your API key is set
echo $OPENAI_API_KEY

# If using .env file, make sure python-dotenv loads it
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Database Issues
```bash
# Remove old database
rm youfyi.db test.db test_rag.db

# Recreate on next run
uvicorn app.main:app --reload
```

### Import Errors
```bash
# Ensure you're in the correct directory
cd /home/saurabh/You.Fyi

# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## API Testing with cURL Examples

See example usage section above for complete cURL commands.

## Support

For issues or questions, check:
1. API docs at `http://localhost:8000/docs`
2. Test files for usage examples
3. Check that OPENAI_API_KEY is properly set for LLM features

## License

Built for You.fyi
