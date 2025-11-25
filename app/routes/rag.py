from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Kit, SharingLink
from app.schemas import RagQueryRequest, RagQueryResponse
from app.services.rag import RAGService
from datetime import datetime

router = APIRouter(prefix="/rag", tags=["rag"])

def fmt_size(n):
    """Format file size in human readable format"""
    if not n and n != 0:
        return '-'
    if n < 1024:
        return str(n) + ' B'
    if n < 1024 * 1024:
        return f"{(n / 1024):.1f} KB"
    return f"{(n / 1024 / 1024):.2f} MB"


@router.post("/query", response_model=RagQueryResponse)
def query_rag(request: RagQueryRequest, db: Session = Depends(get_db)):
    """
    Query a kit's assets using RAG with a selected LLM.
    """
    if not request.kit_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A kit_id must be provided to run a RAG query."
        )
    
    kit = db.query(Kit).filter(Kit.id == request.kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    if not kit.assets:
        raise HTTPException(status_code=400, detail="Kit has no assets")
    
    model_to_use = request.model or "gemini-pro"

    # Handle quick queries (no LLM required)
    if model_to_use == "none" or request.query in ["Count Assets", "File Types", "Recent Files", "Basic Summary", "Largest Files", "List PDFs", "List Images"]:
        try:
            import json
            
            # Helper to serialize asset
            def serialize_asset(a):
                return {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "mime_type": a.mime_type,
                    "file_size": a.file_size,
                    "asset_type": a.asset_type,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                }

            if request.query == "Count Assets":
                assets = kit.assets
                total_size = sum((a.file_size or 0) for a in assets)
                types = list(set(a.mime_type for a in assets if a.mime_type))
                answer = f"You have {len(assets)} assets in this workspace with a total size of {fmt_size(total_size)}. File types include: {', '.join(types) or 'None'}"
                sources = [a.id for a in assets]
            
            elif request.query == "File Types":
                assets = kit.assets
                type_groups = {}
                for a in assets:
                    type_name = a.mime_type or 'Unknown'
                    if type_name not in type_groups:
                        type_groups[type_name] = []
                    type_groups[type_name].append(a.name)

                answer = "Asset types in this workspace:\n\n"
                for type_name, files in type_groups.items():
                    answer += f"{type_name}: {len(files)} files\n"
                    for filename in files:
                        answer += f"  - {filename}\n"
                sources = [a.id for a in assets]
            
            elif request.query == "Basic Summary":
                assets = kit.assets
                total_size = sum((a.file_size or 0) for a in assets)
                types = list(set(a.mime_type for a in assets if a.mime_type))
                kits_count = len(kit.workspace.kits) if kit.workspace else 0

                answer = f"Workspace Summary:\n\n" + \
                        f"• Total Assets: {len(assets)}\n" + \
                        f"• Total Size: {fmt_size(total_size)}\n" + \
                        f"• File Types: {', '.join(types) or 'None'}\n" + \
                        f"• Kits Available: {kits_count}\n\n" + \
                        "Asset Details:\n" + \
                        "\n".join(f"• {a.name} ({fmt_size(a.file_size)}) - {a.mime_type or 'Unknown'}" for a in assets)
                sources = [a.id for a in assets]

            # --- Structured Responses (JSON) ---
            elif request.query == "Recent Files":
                assets = sorted(kit.assets, key=lambda x: x.created_at or '', reverse=True)[:5]
                answer = json.dumps([serialize_asset(a) for a in assets])
                sources = [a.id for a in assets]
            
            elif request.query == "Largest Files":
                assets = sorted(kit.assets, key=lambda x: x.file_size or 0, reverse=True)[:5]
                answer = json.dumps([serialize_asset(a) for a in assets])
                sources = [a.id for a in assets]

            elif request.query == "List PDFs":
                assets = [a for a in kit.assets if a.mime_type == 'application/pdf']
                answer = json.dumps([serialize_asset(a) for a in assets])
                sources = [a.id for a in assets]

            elif request.query == "List Images":
                assets = [a for a in kit.assets if a.mime_type and a.mime_type.startswith('image/')]
                answer = json.dumps([serialize_asset(a) for a in assets])
                sources = [a.id for a in assets]
            
            else:
                # Fall back to LLM queries for other cases
                answer, sources = RAGService.retrieve_and_answer(
                    query=request.query,
                    assets=kit.assets,
                    use_llm=request.use_llm,
                    model=model_to_use
                )

            return RagQueryResponse(
                query=request.query,
                answer=answer,
                sources=sources,
                model="quick-query" if model_to_use == "none" else model_to_use
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
    else:
        # LLM-based queries
        try:
            answer, sources = RAGService.retrieve_and_answer(
                query=request.query,
                assets=kit.assets,
                use_llm=request.use_llm,
                model=model_to_use
            )

            return RagQueryResponse(
                query=request.query,
                answer=answer,
                sources=sources,
                model=model_to_use
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/query/shared/{token}", response_model=RagQueryResponse)
def query_rag_via_sharing_link(token: str, request: RagQueryRequest, db: Session = Depends(get_db)):
    """
    Query a kit's assets using a sharing link token.
    """
    link = db.query(SharingLink).filter(SharingLink.token == token).first()
    if not link:
        raise HTTPException(status_code=404, detail="Sharing link not found")
    
    if not link.is_active or (link.expires_at and link.expires_at < datetime.utcnow()):
        raise HTTPException(status_code=403, detail="Sharing link is inactive or has expired")
    
    kit = link.kit
    if not kit.assets:
        raise HTTPException(status_code=400, detail="Kit has no assets")
    
    model_to_use = request.model or "gemini-pro"

    try:
        answer, sources = RAGService.retrieve_and_answer(
            query=request.query,
            assets=kit.assets,
            use_llm=request.use_llm,
            model=model_to_use
        )
        
        return RagQueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            model=model_to_use
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
