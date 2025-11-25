import requests
import sys
import json

BASE_URL = "http://localhost:8001"

def check(response, msg):
    if response.status_code >= 400:
        print(f"FAILED: {msg} - {response.status_code} {response.text}")
        sys.exit(1)
    print(f"PASSED: {msg}")
    return response.json()

def run_verification():
    print("Starting UI Refinement Verification...")

    import time
    # 1. Create Workspace
    ws_data = {"name": f"UI Test WS {int(time.time())}", "description": "For UI verification"}
    ws = check(requests.post(f"{BASE_URL}/workspaces/", json=ws_data), "Create Workspace")
    ws_id = ws["id"]

    # 2. Create Assets
    asset1 = check(requests.post(f"{BASE_URL}/assets/{ws_id}", json={
        "name": "Doc 1", "content": "Content 1", "asset_type": "document"
    }), "Create Asset 1")
    
    asset2 = check(requests.post(f"{BASE_URL}/assets/{ws_id}", json={
        "name": "Image 1", "content": "fake-image-content", "asset_type": "image"
    }), "Create Asset 2")
    # Hack to simulate image mime type since we can't easily upload here without a file
    # We'll just rely on "Recent Files" for now which should return all.

    # 3. Create Kit
    kit_data = {"name": "UI Kit", "asset_ids": [asset1["id"], asset2["id"]]}
    kit = check(requests.post(f"{BASE_URL}/kits/{ws_id}", json=kit_data), "Create Kit")
    kit_id = kit["id"]

    # 4. Test "Recent Files" (Should be JSON)
    res = requests.post(f"{BASE_URL}/rag/query", json={
        "query": "Recent Files",
        "kit_id": kit_id,
        "use_llm": False,
        "model": "none"
    })
    data = check(res, "Query Recent Files")
    
    try:
        parsed = json.loads(data["answer"])
        if not isinstance(parsed, list):
            print("FAILED: Answer is not a JSON list")
            sys.exit(1)
        print(f"PASSED: Answer is a JSON list with {len(parsed)} items")
        print("Sample item:", parsed[0])
    except json.JSONDecodeError:
        print(f"FAILED: Answer is not valid JSON: {data['answer']}")
        sys.exit(1)

    print("\nVerification Successful!")

if __name__ == "__main__":
    try:
        run_verification()
    except requests.exceptions.ConnectionError:
        print("FAILED: Could not connect to server. Is it running?")
        sys.exit(1)
