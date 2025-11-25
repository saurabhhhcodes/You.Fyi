#!/usr/bin/env bash
# You.fyi Project - Quick Command Reference
# Location: /home/saurabh/You.Fyi

# ============================================
# SETUP
# ============================================

# 1. Navigate to project
cd /home/saurabh/You.Fyi

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set OpenAI API Key
export OPENAI_API_KEY="sk-proj-..."

# ============================================
# RUNNING TESTS
# ============================================

# Run all tests
pytest tests/ -v

# Run only API tests
pytest tests/test_api.py -v

# Run only RAG tests
pytest tests/test_rag.py -v

# Run specific test class
pytest tests/test_api.py::TestKits -v

# Run specific test
pytest tests/test_api.py::TestKits::test_create_kit -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html
# Then open: htmlcov/index.html

# Run with markers
pytest tests/ -m "slow" -v

# ============================================
# RUNNING SERVER
# ============================================

# Start development server
uvicorn app.main:app --reload

# Start on different port
uvicorn app.main:app --reload --port 8001

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000

# ============================================
# API EXAMPLES (with curl)
# ============================================

# Create workspace
curl -X POST http://localhost:8000/workspaces/ \
  -H "Content-Type: application/json" \
  -d '{"name":"MyProject","description":"Test"}'

# Get workspace ID from response, then:

# Create asset
curl -X POST http://localhost:8000/assets/{workspace_id} \
  -H "Content-Type: application/json" \
  -d '{"name":"Doc","content":"Test content","asset_type":"document"}'

# Create kit
curl -X POST http://localhost:8000/kits/{workspace_id} \
  -H "Content-Type: application/json" \
  -d '{"name":"Kit1","asset_ids":["asset_id"]}'

# Query with LLM
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is Python?","kit_id":"kit_id","use_llm":true}'

# ============================================
# DOCUMENTATION
# ============================================

# View API documentation (after starting server)
# http://localhost:8000/docs

# View ReDoc
# http://localhost:8000/redoc

# Read main docs
cat README.md

# Read testing guide
cat TESTING.md

# Read project summary
cat COMPLETED.md

# ============================================
# DATABASE
# ============================================

# View SQLite database
sqlite3 youfyi.db ".tables"

# Reset database (delete)
rm youfyi.db test.db

# ============================================
# DEBUGGING
# ============================================

# Run tests with print output
pytest tests/test_api.py -v -s

# Run with verbose error details
pytest tests/test_api.py -vv --tb=long

# Run single test with debugging
pytest tests/test_api.py::TestKits::test_create_kit -vv -s

# Check Python version
python3 --version

# Check installed packages
pip list

# Check if dependencies are installed
python3 -c "import fastapi; import sqlalchemy; print('All good!')"

# ============================================
# USEFUL ONE-LINERS
# ============================================

# Complete setup and test
./setup.sh

# Quick test run
pytest tests/test_api.py -v && echo "✅ All tests passed!"

# Count test functions
grep -r "def test_" tests/ | wc -l

# List all endpoints
grep -r "@router\." app/routes/ | grep -E "(post|get|put|delete)"

# Check code statistics
find app -name "*.py" -exec wc -l {} + | tail -1

# ============================================
# TROUBLESHOOTING
# ============================================

# Fix: ModuleNotFoundError
pip install -r requirements.txt

# Fix: OPENAI_API_KEY not found
echo "OPENAI_API_KEY=your-key" > .env
source .env

# Fix: Database locked
rm *.db

# Fix: Port already in use
lsof -i :8000  # Check what's using port
kill -9 <PID>   # Kill the process

# ============================================
# ENVIRONMENT VARIABLES
# ============================================

# Set API key for session
export OPENAI_API_KEY="sk-proj-..."

# Or create .env file
cat > .env << EOF
OPENAI_API_KEY=sk-proj-your-key-here
DATABASE_URL=sqlite:///./youfyi.db
DEBUG=True
EOF

# ============================================
# PROJECT INFO
# ============================================

# Show project structure
tree -L 2 -I '__pycache__'

# Show all Python files
find . -name "*.py" -type f

# Count lines of code
find app -name "*.py" -exec wc -l {} + | tail -1

# List all tests
pytest --collect-only tests/

# ============================================
# CLEANUP
# ============================================

# Remove pycache
find . -type d -name __pycache__ -exec rm -rf {} +

# Remove pytest cache
rm -rf .pytest_cache

# Remove databases
rm *.db

# Clean all
find . -type f -name "*.pyc" -delete
find . -type d -name __pycache__ -delete
rm -rf .pytest_cache
rm *.db

# ============================================
# GIT COMMANDS
# ============================================

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Add to repository
git remote add origin https://github.com/user/you-fyi.git
git push -u origin main

# ============================================
# DEPLOYMENT
# ============================================

# Docker build
docker build -t youfyi:latest .

# Docker run
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... youfyi:latest

# AWS deployment
# See deployment guides in README.md

# ============================================
# MONITORING
# ============================================

# Run with logging
pytest tests/ -v --log-cli-level=DEBUG

# Monitor server in production
# Use tools like PM2, Supervisor, or Gunicorn

# ============================================
# BACKUP
# ============================================

# Backup database
cp youfyi.db youfyi.db.backup

# Backup entire project
tar -czf youfyi-backup.tar.gz .

# ============================================
# SUMMARY
# ============================================

# All tests passing
pytest tests/ -v --tb=short

# Server running
uvicorn app.main:app --reload

# API documentation
open http://localhost:8000/docs

# Ready to submit!
echo "✅ Project ready for submission!"

# ============================================
# QUICK START (One Command)
# ============================================

cd /home/saurabh/You.Fyi && \
source venv/bin/activate 2>/dev/null || (python3 -m venv venv && source venv/bin/activate) && \
pip install -r requirements.txt -q && \
export OPENAI_API_KEY="your-key" && \
pytest tests/test_api.py -v && \
echo "✅ Ready! Run: uvicorn app.main:app --reload"
