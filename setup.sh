#!/bin/bash

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}You.fyi - Smart Workspace with RAG${NC}"
echo -e "${BLUE}===============================================${NC}"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt -q

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env and add your OPENAI_API_KEY${NC}"
fi

# Load env
export $(cat .env | grep -v '#' | xargs)

echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo -e "${BLUE}To run the server:${NC}"
echo -e "${BLUE}  uvicorn app.main:app --reload${NC}"
echo ""
echo -e "${BLUE}To run tests:${NC}"
echo -e "${BLUE}  pytest tests/ -v${NC}"
echo ""
echo -e "${BLUE}To run tests with LLM:${NC}"
echo -e "${BLUE}  pytest tests/test_rag.py -v${NC}"
echo ""
echo -e "${GREEN}Quick Test${NC}"
echo "Testing imports..."

python3 -c "from app.main import app; from app.services import LLMService; print('✓ All imports OK')" && \
echo -e "${GREEN}Ready to go!${NC}" || \
echo -e "${YELLOW}Warning: Some imports failed${NC}"
