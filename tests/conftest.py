import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def test_db():
    """Create a fresh test database for the session"""
    test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    test_db_file.close()
    
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{test_db_file.name}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    
    Base.metadata.create_all(bind=engine)
    yield engine
    
    # Cleanup
    os.unlink(test_db_file.name)


@pytest.fixture
def db_session(test_db):
    """Create a fresh database session for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    
    # Clear all tables before each test
    Base.metadata.drop_all(bind=test_db)
    Base.metadata.create_all(bind=test_db)
    
    connection = test_db.connect()
    transaction = connection.begin()
    
    session = TestingSessionLocal(bind=connection)
    
    def override_get_db():
        yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
    
    # Remove override
    app.dependency_overrides.pop(get_db, None)


from fastapi.testclient import TestClient

@pytest.fixture
def client(db_session):
    """Return a TestClient that uses the overridden db_session"""
    return TestClient(app)
