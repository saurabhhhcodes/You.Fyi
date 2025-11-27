import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
import uuid

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_get_all_shared_links(test_db):
    # 1. Create Workspace
    ws_name = f"WS_Shared_{uuid.uuid4().hex}"
    res = client.post("/workspaces/", json={"name": ws_name, "description": "desc"})
    assert res.status_code == 201
    ws_id = res.json()["id"]

    # 2. Create Kit
    res = client.post(f"/kits/{ws_id}", json={"name": "Kit1", "description": "desc"})
    assert res.status_code == 201
    kit_id = res.json()["id"]

    # 3. Create Workspace Link
    res = client.post(f"/sharing-links/workspace/{ws_id}", json={"expires_in_days": 7})
    assert res.status_code == 201
    ws_link_token = res.json()["token"]

    # 4. Create Kit Link
    res = client.post(f"/sharing-links/kit/{kit_id}", json={"expires_in_days": 7})
    assert res.status_code == 201
    kit_link_token = res.json()["token"]

    # 5. Get All Shared Links
    res = client.get(f"/workspaces/{ws_id}/shared-links")
    assert res.status_code == 200
    data = res.json()

    # Verify Workspace Links
    assert len(data["workspace_links"]) == 1
    assert data["workspace_links"][0]["token"] == ws_link_token

    # Verify Kit Links
    assert len(data["kit_links"]) == 1
    assert data["kit_links"][0]["kit_id"] == kit_id
    assert len(data["kit_links"][0]["links"]) == 1
    assert data["kit_links"][0]["links"][0]["token"] == kit_link_token

    print("Shared links verification passed!")
