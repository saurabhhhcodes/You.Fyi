CLIENT QUICKSTART — You.fyi

This file explains how your client can use the product features quickly and confidently.

1) Prerequisites
- A machine with `curl`, `python3` and `pip` installed.
- If using LLM/RAG features, set `OPENAI_API_KEY` on the server (server reads it, client does not need it).
- If running locally, ensure the server is started:

```bash
pip install -r requirements.txt
export OPENAI_API_KEY='sk-your-key'      # only if you want server to call OpenAI
uvicorn app.main:app --reload --port 8001
```

2) Quick demonstration (client can run this locally)
- Run the demo script shipped with the repo. It will:
  - Create a workspace
  - Create a text asset
  - Create and upload a small PDF (or you can pass a file path)
  - Create a kit and add assets to it
  - Create a sharing link (7-day expiry)
  - Run a RAG query (uses server's OpenAI key if set)

Usage:

```bash
# (Optional) point to deployed server
# BASE_URL=https://youfyi-xxxxx.onrender.com ./client_demo.sh /path/to/file.pdf

# Default (local)
./client_demo.sh
```

3) How to use core features (examples)

- Create workspace:
```
curl -X POST http://localhost:8001/workspaces/ \
  -H "Content-Type: application/json" \
  -d '{"name":"My Project","description":"My description"}'
```

- Upload file:
```
curl -X POST http://localhost:8001/assets/{workspace_id}/upload \
  -F "file=@document.pdf" \
  -F "description=User manual"
```

- Create a kit:
```
curl -X POST http://localhost:8001/kits/{workspace_id} \
  -H "Content-Type: application/json" \
  -d '{"name":"Release Kit","description":"All assets for release"}'
```

- Add assets to kit:
```
curl -X PUT http://localhost:8001/kits/kit/{kit_id} \
  -H "Content-Type: application/json" \
  -d '{"asset_ids":["asset1","asset2"]}'
```

- Create a sharing link:
```
curl -X POST http://localhost:8001/sharing-links/kit/{kit_id} -H "Content-Type: application/json" -d '{"expires_in_days":7}'
```

- Run RAG query:
```
curl -X POST http://localhost:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Summarize the kit","kit_id":"{kit_id}","use_llm":true}'
```

4) Postman / integration
- If your client prefers Postman, import the OpenAPI schema at `http://localhost:8001/openapi.json` (or `{DEPLOY_URL}/openapi.json`). This will create ready-to-run requests.

5) Support & Handoff
- Send the client `CLIENT_INSTRUCTIONS.md`, `QUICK_START.md`, and `FIVERR_SUBMISSION.md`.
- If the client wants UI or a hosted front-end, I can create a small web UI to consume the API for them.

6) Notes for the client
- LLM calls require the server to have `OPENAI_API_KEY` set. The client does not need to have the key on their local machine to run the demo (unless they run the LLM calls locally).
- Uploaded files are stored according to the app's storage config; if deploying to Render or another host, ensure persistent storage or S3 is configured for production.
