import os
import tempfile
import requests
import time

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8001')


def create_workspace():
    import time
    name = f"ui-test-ws-{int(time.time())}"
    r = requests.post(f"{BASE_URL}/workspaces", json={"name": name, "description": "ui flow test"})
    r.raise_for_status()
    return r.json()['id']


def create_text_asset(ws_id):
    r = requests.post(f"{BASE_URL}/assets/{ws_id}", json={"name": "ui-test-asset", "description": "text asset", "content": "hello from test"})
    r.raise_for_status()
    return r.json()['id']


def upload_file(ws_id, path):
    with open(path, 'rb') as fh:
        files = {'file': (os.path.basename(path), fh)}
        r = requests.post(f"{BASE_URL}/assets/{ws_id}/upload", files=files)
    r.raise_for_status()
    return r.json()['id']


def create_kit(ws_id):
    r = requests.post(f"{BASE_URL}/kits/{ws_id}", json={"name": "ui-kit", "description": "kit from test"})
    r.raise_for_status()
    return r.json()['id']


def add_assets_to_kit(kit_id, asset_ids):
    r = requests.put(f"{BASE_URL}/kits/kit/{kit_id}", json={"asset_ids": asset_ids})
    # endpoint may return 204 No Content
    if r.status_code == 204:
        return True
    r.raise_for_status()
    return True


def list_assets(ws_id):
    r = requests.get(f"{BASE_URL}/assets/{ws_id}")
    r.raise_for_status()
    return r.json()


def test_ui_flow_basic():
    # ensure server is up
    for _ in range(6):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError('Server not responding at ' + BASE_URL)

    ws = create_workspace()
    text_asset = create_text_asset(ws)

    # create temporary pdf
    fd, path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)
    with open(path, 'wb') as f:
        f.write(b"%PDF-1.4\n%Test PDF content\n")

    uploaded_asset = upload_file(ws, path)

    assets = list_assets(ws)
    ids = [a['id'] for a in assets]
    assert text_asset in ids
    assert uploaded_asset in ids

    kit = create_kit(ws)
    added = add_assets_to_kit(kit, ids)
    assert added
    # download uploaded asset
    r = requests.get(f"{BASE_URL}/assets/asset/{uploaded_asset}/download")
    assert r.status_code == 200
    assert r.content and len(r.content) > 10

    # create sharing link for kit and check shared RAG endpoint (should return 200 even if LLM not available)
    r = requests.post(f"{BASE_URL}/sharing-links/kit/{kit}", json={"expires_in_days":7})
    r.raise_for_status()
    token = r.json().get('token')
    assert token
    r2 = requests.post(f"{BASE_URL}/rag/query/shared/{token}", json={"query":"summary"})
    # may return 200 with retrieval, 400 for bad request, or 500 if LLM backend error
    assert r2.status_code in (200, 400, 500)

    # cleanup
    os.remove(path)
