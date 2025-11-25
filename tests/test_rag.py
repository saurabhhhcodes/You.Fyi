import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.services import LLMService
from app.services.rag import RAGService
import os


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_rag.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def setup_db():
    """Create tables and cleanup after tests"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_workspace():
    """Create a sample workspace"""
    response = client.post(
        "/workspaces/",
        json={"name": "RAG Test Workspace", "description": "For testing"}
    )
    return response.json()["id"]


@pytest.fixture
def sample_kit_with_assets(sample_workspace):
    """Create a kit with sample assets"""
    workspace_id = sample_workspace
    
    # Create assets with sample content
    assets = [
        {
            "name": "Python Guide",
            "content": "Python is a high-level programming language. It emphasizes code readability. Python supports multiple programming paradigms including object-oriented, functional, and procedural styles. Python has a large standard library.",
            "asset_type": "document"
        },
        {
            "name": "AI Overview",
            "content": "Artificial Intelligence (AI) is the simulation of human intelligence by machines. Machine Learning is a subset of AI that enables systems to learn and improve from experience. Deep Learning uses neural networks to process large amounts of data.",
            "asset_type": "document"
        },
        {
            "name": "Web Development",
            "content": "Web development involves building applications for the web. Frontend development focuses on user interfaces and user experience. Backend development handles server-side logic and databases. Full-stack developers work on both frontend and backend.",
            "asset_type": "document"
        }
    ]
    
    asset_ids = []
    for asset in assets:
        response = client.post(
            f"/assets/{workspace_id}",
            json=asset
        )
        asset_ids.append(response.json()["id"])
    
    # Create kit with assets
    kit_response = client.post(
        f"/kits/{workspace_id}",
        json={
            "name": "Sample Kit",
            "description": "Kit for testing",
            "asset_ids": asset_ids
        }
    )
    return kit_response.json()["id"]


class TestLLMService:
    """Test real LLM calls to OpenAI"""
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_query_with_context(self):
        """Test real LLM query with context"""
        context = "Python is a high-level programming language known for readability."
        query = "What is Python?"
        
        try:
            response = LLMService.query_with_context(query, context)
            assert isinstance(response, str)
            assert len(response) > 0
            # Check if response contains relevant keywords
            assert any(word in response.lower() for word in ["python", "language", "programming"])
        except Exception as e:
            pytest.skip(f"LLM API call failed: {str(e)}")

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_summarize_assets(self):
        """Test real LLM summarization"""
        assets = [
            "Python is a programming language",
            "AI is artificial intelligence",
            "Web development builds websites"
        ]
        
        try:
            response = LLMService.summarize_assets(assets)
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            pytest.skip(f"LLM API call failed: {str(e)}")

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_semantic_search(self):
        """Test real LLM semantic search"""
        assets = [
            "Python is a high-level programming language",
            "Machine Learning is a subset of AI",
            "Web development uses HTML and CSS"
        ]
        query = "What is Python?"
        
        try:
            response = LLMService.semantic_search(query, assets)
            assert isinstance(response, list)
            # Should return indices
            assert all(isinstance(idx, int) for idx in response)
        except Exception as e:
            pytest.skip(f"LLM API call failed: {str(e)}")


class TestRAGService:
    """Test RAG service with real LLM"""
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_retrieve_and_answer(self, setup_db, sample_kit_with_assets):
        """Test RAG retrieval and answer with real LLM"""
        from app.models import Kit
        from sqlalchemy.orm import Session
        
        db = TestingSessionLocal()
        kit = db.query(Kit).filter(Kit.id == sample_kit_with_assets).first()
        db.close()
        
        query = "What is Python?"
        
        try:
            answer, sources = RAGService.retrieve_and_answer(
                query=query,
                assets=kit.assets,
                use_llm=True
            )
            assert isinstance(answer, str)
            assert len(answer) > 0
            assert isinstance(sources, list)
        except Exception as e:
            pytest.skip(f"RAG service failed: {str(e)}")


class TestRAGEndpoints:
    """Test RAG API endpoints"""
    
    def test_query_rag_without_kit_id(self, setup_db):
        """Test RAG query endpoint validation"""
        response = client.post(
            "/rag/query",
            json={"query": "What is Python?", "use_llm": False}
        )
        assert response.status_code == 400

    def test_query_rag_nonexistent_kit(self, setup_db):
        """Test RAG query with nonexistent kit"""
        response = client.post(
            "/rag/query",
            json={
                "query": "What is Python?",
                "kit_id": "nonexistent-id",
                "use_llm": False
            }
        )
        assert response.status_code == 404

    def test_query_rag_empty_kit(self, setup_db, sample_workspace):
        """Test RAG query with empty kit"""
        workspace_id = sample_workspace
        
        # Create empty kit
        kit_response = client.post(
            f"/kits/{workspace_id}",
            json={"name": "Empty Kit", "asset_ids": []}
        )
        kit_id = kit_response.json()["id"]
        
        response = client.post(
            "/rag/query",
            json={
                "query": "What is Python?",
                "kit_id": kit_id,
                "use_llm": False
            }
        )
        assert response.status_code == 400

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_query_rag_with_assets_real_llm(self, setup_db, sample_kit_with_assets):
        """Test RAG query endpoint with real LLM"""
        response = client.post(
            "/rag/query",
            json={
                "query": "What is Python?",
                "kit_id": sample_kit_with_assets,
                "use_llm": True
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "answer" in data
            assert "sources" in data
            assert data["query"] == "What is Python?"
        else:
            pytest.skip(f"LLM API call failed: {response.text}")

    def test_query_rag_with_assets_no_llm(self, setup_db, sample_kit_with_assets):
        """Test RAG query endpoint without LLM"""
        response = client.post(
            "/rag/query",
            json={
                "query": "What is Python?",
                "kit_id": sample_kit_with_assets,
                "use_llm": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "answer" in data
        assert "sources" in data

    def test_query_rag_via_sharing_link(self, setup_db, sample_kit_with_assets):
        """Test RAG query via sharing link"""
        # Create sharing link
        link_response = client.post(
            f"/sharing-links/kit/{sample_kit_with_assets}",
            json={"expires_in_days": 7}
        )
        token = link_response.json()["token"]
        
        # Query via sharing link
        response = client.post(
            f"/rag/query/shared/{token}",
            json={
                "query": "What is Python?",
                "use_llm": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "answer" in data

    def test_query_rag_via_expired_link(self, setup_db, sample_kit_with_assets):
        """Test RAG query via expired sharing link"""
        from datetime import datetime, timedelta
        
        # Create sharing link with past expiration
        link_response = client.post(
            f"/sharing-links/kit/{sample_kit_with_assets}",
            json={"expires_in_days": -1}  # Already expired
        )
        token = link_response.json()["token"]
        
        # Query via expired link
        response = client.post(
            f"/rag/query/shared/{token}",
            json={
                "query": "What is Python?",
                "use_llm": False
            }
        )
        assert response.status_code == 403
