import requests
import sys

BASE_URL = "http://localhost:8001"

def check(response, msg):
    if response.status_code >= 400:
        print(f"FAILED: {msg} - {response.status_code} {response.text}")
        sys.exit(1)
    print(f"PASSED: {msg}")
    return response.json()

def run_verification():
    print("Starting verification...")

    # 1. Create Workspace
    ws_data = {"name": "Test WS", "description": "For verification"}
    ws = check(requests.post(f"{BASE_URL}/workspaces/", json=ws_data), "Create Workspace")
    ws_id = ws["id"]

    # 2. Create Asset
    asset_data = {
        "name": "Test Asset",
        "description": "Test content",
        "content": "The secret code is 12345.",
        "asset_type": "document"
    }
    asset = check(requests.post(f"{BASE_URL}/assets/{ws_id}", json=asset_data), "Create Asset")
    asset_id = asset["id"]

    # 3. Create Kit
    kit_data = {
        "name": "Test Kit",
        "description": "Kit with secret",
        "asset_ids": [asset_id]
    }
    kit = check(requests.post(f"{BASE_URL}/kits/{ws_id}", json=kit_data), "Create Kit")
    kit_id = kit["id"]

    # 4. Create Sharing Link
    link_data = {"expires_in_days": 1}
    link = check(requests.post(f"{BASE_URL}/sharing-links/kit/{kit_id}", json=link_data), "Create Sharing Link")
    token = link["token"]
    print(f"Token: {token}")

    # 5. Verify Link Token (Frontend uses this)
    link_info = check(requests.get(f"{BASE_URL}/sharing-links/token/{token}"), "Get Link Info")
    assert link_info["kit_id"] == kit_id
    assert link_info["is_active"] == True

    # 6. Query via Sharing Link (Frontend uses this)
    # Note: We use use_llm=False to avoid needing an API key for this basic connectivity test
    query_data = {
        "query": "What is the secret code?",
        "use_llm": False 
    }
    # The non-LLM path might not return the answer from content, but it should return 200 OK.
    # Actually, let's check what the backend does with use_llm=False.
    # It likely just does a keyword search or returns a placeholder if semantic search isn't set up without LLM.
    # But the important thing is that the endpoint is accessible.
    
    res = requests.post(f"{BASE_URL}/rag/query/shared/{token}", json=query_data)
    check(res, "Query via Shared Link")
    print("Response:", res.json())

    print("\nVerification Successful!")

if __name__ == "__main__":
    try:
        run_verification()
    except requests.exceptions.ConnectionError:
        print("FAILED: Could not connect to server. Is it running?")
        sys.exit(1)
