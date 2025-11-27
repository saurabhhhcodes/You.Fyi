import pytest


class TestWorkspaces:
    def test_create_workspace(self, client):
        response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test Description"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Workspace"
        assert data["description"] == "Test Description"
        assert "id" in data

    def test_list_workspaces(self, client):
        # Create workspaces
        client.post(
            "/workspaces/",
            json={"name": "Workspace 1", "description": "First"}
        )
        client.post(
            "/workspaces/",
            json={"name": "Workspace 2", "description": "Second"}
        )
        
        response = client.get("/workspaces/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_workspace(self, client):
        # Create workspace
        create_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = create_response.json()["id"]
        
        # Get workspace
        response = client.get(f"/workspaces/{workspace_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workspace_id
        assert data["name"] == "Test Workspace"

    def test_get_nonexistent_workspace(self, client):
        response = client.get("/workspaces/nonexistent-id")
        assert response.status_code == 404

    def test_delete_workspace(self, client):
        # Create workspace
        create_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = create_response.json()["id"]
        
        # Delete workspace
        response = client.delete(f"/workspaces/{workspace_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/workspaces/{workspace_id}")
        assert get_response.status_code == 404


class TestAssets:
    def test_create_asset(self, client):
        # Create workspace first
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        # Create asset
        response = client.post(
            f"/assets/{workspace_id}",
            json={
                "name": "Test Asset",
                "description": "Asset Description",
                "content": "This is test content",
                "asset_type": "document"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Asset"
        assert data["content"] == "This is test content"
        assert "id" in data

    def test_list_assets(self, client):
        # Create workspace
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        # Create multiple assets
        client.post(
            f"/assets/{workspace_id}",
            json={
                "name": "Asset 1",
                "content": "Content 1",
                "asset_type": "document"
            }
        )
        client.post(
            f"/assets/{workspace_id}",
            json={
                "name": "Asset 2",
                "content": "Content 2",
                "asset_type": "document"
            }
        )
        
        response = client.get(f"/assets/{workspace_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_asset(self, client):
        # Create workspace and asset
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        asset_response = client.post(
            f"/assets/{workspace_id}",
            json={
                "name": "Test Asset",
                "content": "Test content",
                "asset_type": "document"
            }
        )
        asset_id = asset_response.json()["id"]
        
        response = client.get(f"/assets/asset/{asset_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == asset_id

    def test_delete_asset(self, client):
        # Create workspace and asset
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        asset_response = client.post(
            f"/assets/{workspace_id}",
            json={
                "name": "Test Asset",
                "content": "Test content",
                "asset_type": "document"
            }
        )
        asset_id = asset_response.json()["id"]
        
        # Delete
        response = client.delete(f"/assets/asset/{asset_id}")
        assert response.status_code == 204


class TestKits:
    def test_create_kit(self, client):
        # Create workspace
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        # Create kit
        response = client.post(
            f"/kits/{workspace_id}",
            json={
                "name": "Test Kit",
                "description": "Kit Description",
                "asset_ids": []
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Kit"
        assert "id" in data

    def test_create_kit_with_assets(self, client):
        # Create workspace
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        # Create assets
        asset1_response = client.post(
            f"/assets/{workspace_id}",
            json={
                "name": "Asset 1",
                "content": "Content 1",
                "asset_type": "document"
            }
        )
        asset1_id = asset1_response.json()["id"]
        
        asset2_response = client.post(
            f"/assets/{workspace_id}",
            json={
                "name": "Asset 2",
                "content": "Content 2",
                "asset_type": "document"
            }
        )
        asset2_id = asset2_response.json()["id"]
        
        # Create kit with assets
        response = client.post(
            f"/kits/{workspace_id}",
            json={
                "name": "Test Kit",
                "description": "Kit with assets",
                "asset_ids": [asset1_id, asset2_id]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["assets"]) == 2

    def test_list_kits(self, client):
        # Create workspace
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        # Create kits
        client.post(
            f"/kits/{workspace_id}",
            json={"name": "Kit 1", "asset_ids": []}
        )
        client.post(
            f"/kits/{workspace_id}",
            json={"name": "Kit 2", "asset_ids": []}
        )
        
        response = client.get(f"/kits/{workspace_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_kit(self, client):
        # Create workspace and kit
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        kit_response = client.post(
            f"/kits/{workspace_id}",
            json={"name": "Test Kit", "asset_ids": []}
        )
        kit_id = kit_response.json()["id"]
        
        response = client.get(f"/kits/kit/{kit_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == kit_id

    def test_update_kit(self, client):
        # Create workspace and kit
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        kit_response = client.post(
            f"/kits/{workspace_id}",
            json={"name": "Original Kit", "asset_ids": []}
        )
        kit_id = kit_response.json()["id"]
        
        # Update kit
        response = client.put(
            f"/kits/kit/{kit_id}",
            json={"name": "Updated Kit", "description": "New Description"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Kit"
        assert data["description"] == "New Description"

    def test_delete_kit(self, client):
        # Create workspace and kit
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        kit_response = client.post(
            f"/kits/{workspace_id}",
            json={"name": "Test Kit", "asset_ids": []}
        )
        kit_id = kit_response.json()["id"]
        
        # Delete
        response = client.delete(f"/kits/kit/{kit_id}")
        assert response.status_code == 204


class TestSharingLinks:
    def test_create_sharing_link(self, client):
        # Create workspace and kit
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        kit_response = client.post(
            f"/kits/{workspace_id}",
            json={"name": "Test Kit", "asset_ids": []}
        )
        kit_id = kit_response.json()["id"]
        
        # Create sharing link
        response = client.post(
            f"/sharing-links/kit/{kit_id}",
            json={"expires_in_days": 7}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["kit_id"] == kit_id
        assert data["is_active"] is True
        assert "token" in data

    def test_get_sharing_link_by_token(self, client):
        # Create workspace, kit, and sharing link
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        kit_response = client.post(
            f"/kits/{workspace_id}",
            json={"name": "Test Kit", "asset_ids": []}
        )
        kit_id = kit_response.json()["id"]
        
        link_response = client.post(
            f"/sharing-links/kit/{kit_id}",
            json={"expires_in_days": 7}
        )
        token = link_response.json()["token"]
        
        # Get by token
        response = client.get(f"/sharing-links/token/{token}")
        assert response.status_code == 200
        data = response.json()
        assert data["token"] == token

    def test_deactivate_sharing_link(self, client):
        # Create workspace, kit, and sharing link
        workspace_response = client.post(
            "/workspaces/",
            json={"name": "Test Workspace", "description": "Test"}
        )
        workspace_id = workspace_response.json()["id"]
        
        kit_response = client.post(
            f"/kits/{workspace_id}",
            json={"name": "Test Kit", "asset_ids": []}
        )
        kit_id = kit_response.json()["id"]
        
        link_response = client.post(
            f"/sharing-links/kit/{kit_id}",
            json={"expires_in_days": 7}
        )
        link_id = link_response.json()["id"]
        
        # Deactivate
        response = client.patch(f"/sharing-links/{link_id}/deactivate")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False


class TestIntegration:
    def test_complete_workflow(self, client):
        """Test complete workflow: workspace -> assets -> kit -> sharing link -> RAG query"""
        # Create workspace
        ws = client.post("/workspaces/", json={"name": "Complete Test", "description": "Full workflow"})
        ws_id = ws.json()["id"]
        
        # Create assets
        asset1 = client.post(f"/assets/{ws_id}", json={
            "name": "Doc1", "content": "Python is great", "asset_type": "doc"
        }).json()
        
        asset2 = client.post(f"/assets/{ws_id}", json={
            "name": "Doc2", "content": "AI is the future", "asset_type": "doc"
        }).json()
        
        # Create kit with assets
        kit = client.post(f"/kits/{ws_id}", json={
            "name": "Full Kit", "asset_ids": [asset1["id"], asset2["id"]]
        }).json()
        
        # Create sharing link
        link = client.post(f"/sharing-links/kit/{kit['id']}", json={
            "expires_in_days": 7
        }).json()
        
        # Verify sharing link works
        verify = client.get(f"/sharing-links/token/{link['token']}")
        assert verify.status_code == 200
        
        # Query without LLM
        query = client.post("/rag/query", json={
            "query": "What is Python?",
            "kit_id": kit["id"],
            "use_llm": False
        })
        assert query.status_code == 200
        assert "answer" in query.json()
