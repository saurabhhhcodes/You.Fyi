import requests
import sys

BASE_URL = "http://localhost:8002"

def test_new_features():
    print("Testing New Features...")
    
    # 1. Create Workspaces
    import uuid
    ws1_name = f"WS1_{uuid.uuid4().hex[:8]}"
    ws2_name = f"WS2_{uuid.uuid4().hex[:8]}"
    
    ws1 = requests.post(f"{BASE_URL}/workspaces/", json={"name": ws1_name, "description": "Source"}).json()
    ws2 = requests.post(f"{BASE_URL}/workspaces/", json={"name": ws2_name, "description": "Target"}).json()
    print(f"Created WS1: {ws1['id']}, WS2: {ws2['id']}")

    # 2. Create Asset in WS1
    asset = requests.post(f"{BASE_URL}/assets/{ws1['id']}", json={"name": "A1", "content": "test"}).json()
    print(f"Created Asset: {asset['id']}")

    # 3. Create Kits
    kit1 = requests.post(f"{BASE_URL}/kits/{ws1['id']}", json={"name": "K1"}).json()
    kit2 = requests.post(f"{BASE_URL}/kits/{ws2['id']}", json={"name": "K2"}).json()
    print(f"Created K1: {kit1['id']}, K2: {kit2['id']}")

    # 4. Add Asset to K1
    requests.put(f"{BASE_URL}/kits/kit/{kit1['id']}", json={"asset_ids": [asset['id']]})

    # 5. Workspace Sharing
    link = requests.post(f"{BASE_URL}/sharing-links/workspace/{ws1['id']}", json={"expires_in_days": 7}).json()
    print(f"Created Link: {link['token']}")
    assert link['workspace_id'] == ws1['id']

    # 6. Merge Workspaces (WS1 -> WS2)
    res = requests.post(f"{BASE_URL}/workspaces/merge", json={"source_id": ws1['id'], "target_id": ws2['id']})
    if res.status_code != 200:
        print(f"Merge WS failed: {res.text}")
        sys.exit(1)
    print("Merged WS1 into WS2")

    # Verify WS1 deleted
    res = requests.get(f"{BASE_URL}/workspaces/{ws1['id']}")
    assert res.status_code == 404
    print("Verified WS1 deleted")

    # Verify K1 moved to WS2
    res = requests.get(f"{BASE_URL}/kits/kit/{kit1['id']}")
    print(f"Get Kit Status: {res.status_code}")
    k1_check = res.json()
    print(f"Get Kit Response: {k1_check}")
    assert k1_check['workspace_id'] == ws2['id']
    print("Verified K1 moved")

    # 7. Merge Kits (K1 -> K2)
    res = requests.post(f"{BASE_URL}/kits/merge", json={"source_ids": [kit1['id']], "target_id": kit2['id']})
    if res.status_code != 200:
        print(f"Merge Kits failed: {res.text}")
        sys.exit(1)
    print("Merged K1 into K2")

    # Verify K1 deleted
    res = requests.get(f"{BASE_URL}/kits/kit/{kit1['id']}")
    assert res.status_code == 404
    print("Verified K1 deleted")

    # Verify K2 has asset
    k2_check = requests.get(f"{BASE_URL}/kits/kit/{kit2['id']}").json()
    assert len(k2_check['assets']) > 0
    # The asset ID might be the same or different depending on implementation? 
    # In my implementation, I appended the asset object. The asset ID stays same.
    found = False
    for a in k2_check['assets']:
        if a['id'] == asset['id']:
            found = True
            break
    assert found
    print("Verified K2 has asset")

    print("ALL NEW FEATURES PASSED")

if __name__ == "__main__":
    test_new_features()
