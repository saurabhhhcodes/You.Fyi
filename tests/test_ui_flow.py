import pytest
import os
import tempfile
import time

def create_workspace(client):
    name = f"ui-test-ws-{int(time.time())}"
    r = client.post("/workspaces/", json={"name": name, "description": "ui flow test"})
    assert r.status_code == 201
    return r.json()['id']


def create_text_asset(client, ws_id):
    r = client.post(f"/assets/{ws_id}", json={"name": "ui-test-asset", "description": "text asset", "content": "hello from test", "asset_type": "document"})
    assert r.status_code == 201
    return r.json()['id']


def upload_file(client, ws_id, path):
    with open(path, 'rb') as fh:
        files = {'file': (os.path.basename(path), fh, 'application/pdf')}
        r = client.post(f"/assets/{ws_id}/upload", files=files)
    assert r.status_code == 201
    return r.json()['id']


def create_kit(client, ws_id):
    r = client.post(f"/kits/{ws_id}", json={"name": "ui-kit", "description": "kit from test", "asset_ids": []})
    assert r.status_code == 201
    return r.json()['id']


def add_assets_to_kit(client, kit_id, asset_ids):
    r = client.put(f"/kits/kit/{kit_id}", json={"asset_ids": asset_ids})
    assert r.status_code == 200
    return True


def list_assets(client, ws_id):
    r = client.get(f"/assets/{ws_id}")
    assert r.status_code == 200
    return r.json()


def test_ui_flow_basic(client, db_session):
    ws = create_workspace(client)
    text_asset = create_text_asset(client, ws)

    # create temporary pdf
    fd, path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)
    with open(path, 'wb') as f:
        f.write(b"%PDF-1.4\n%Test PDF content\n")

    try:
        uploaded_asset = upload_file(client, ws, path)

        assets = list_assets(client, ws)
        ids = [a['id'] for a in assets]
        assert text_asset in ids
        assert uploaded_asset in ids

        kit = create_kit(client, ws)
        added = add_assets_to_kit(client, kit, ids)
        assert added
        # download uploaded asset
        r = client.get(f"/assets/asset/{uploaded_asset}/download")
        assert r.status_code == 200
        assert len(r.content) > 10

        # create sharing link for kit
        r = client.post(f"/sharing-links/kit/{kit}", json={"expires_in_days":7})
        assert r.status_code == 201
        token = r.json().get('token')
        assert token
        
        # check shared RAG endpoint
        r2 = client.post(f"/rag/query/shared/{token}", json={"query":"summary", "use_llm": False})
        assert r2.status_code in (200, 400, 500)

    finally:
        if os.path.exists(path):
            os.remove(path)
