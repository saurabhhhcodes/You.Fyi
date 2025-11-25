from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Asset, Workspace
from app.schemas import AssetCreate, AssetRead

router = APIRouter(prefix="/assets", tags=["assets"])


from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Asset, Workspace
from app.schemas import AssetCreate, AssetRead, AssetUpload
import base64
from typing import Optional

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/{workspace_id}", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(workspace_id: str, asset: AssetCreate, db: Session = Depends(get_db)):
    """Create a new asset in a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    db_asset = Asset(workspace_id=workspace_id, **asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.post("/{workspace_id}/upload", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    workspace_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a file to a workspace as an asset.
    
    Supports:
    - Images: .jpg, .jpeg, .png, .gif, .webp, .svg, .bmp
    - Videos: .mp4, .avi, .mov, .mkv, .webm, .flv, .wmv
    - Documents: .pdf, .docx, .doc, .xlsx, .xls, .pptx, .txt, .csv
    - Code/Executables: .exe, .py, .js, .java, .cpp, .c, .sh, .bat
    - Archives: .zip, .rar, .tar, .gz, .7z
    - Any other file type
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Read file content
    contents = await file.read()
    
    # Convert to base64 for storage
    file_content_b64 = base64.b64encode(contents).decode('utf-8')
    
    # Determine asset type from mime type
    mime_type = file.content_type or "application/octet-stream"
    asset_type = _determine_asset_type(mime_type)
    
    # Create asset
    db_asset = Asset(
        workspace_id=workspace_id,
        name=file.filename or "uploaded_file",
        description=description,
        content=file_content_b64,
        asset_type=asset_type,
        mime_type=mime_type,
        file_size=len(contents),
        file_path=file.filename
    )
    
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.get("/{workspace_id}", response_model=list[AssetRead])
def list_assets(workspace_id: str, db: Session = Depends(get_db)):
    """List all assets in a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return db.query(Asset).filter(Asset.workspace_id == workspace_id).all()


@router.get("/asset/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    """Get a specific asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.get("/asset/{asset_id}/download")
def download_asset(asset_id: str, db: Session = Depends(get_db)):
    """Download a file asset"""
    from fastapi.responses import StreamingResponse
    import io
    
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Decode base64 content
    try:
        file_content = base64.b64decode(asset.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to decode file content")
    
    # Create file-like object
    file_obj = io.BytesIO(file_content)
    
    return StreamingResponse(
        iter([file_content]),
        media_type=asset.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={asset.file_path or asset.name}"}
    )


@router.delete("/asset/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: str, db: Session = Depends(get_db)):
    """Delete an asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return None


def _determine_asset_type(mime_type: str) -> str:
    """Determine asset type based on mime type"""
    if mime_type.startswith("image/"):
        return "image"
    elif mime_type.startswith("video/"):
        return "video"
    elif mime_type.startswith("audio/"):
        return "audio"
    elif mime_type == "application/pdf" or mime_type.startswith("application/vnd"):
        return "document"
    elif mime_type == "text/plain" or mime_type == "text/csv":
        return "document"
    elif mime_type in ["application/x-executable", "application/x-msdownload", "application/x-elf"]:
        return "executable"
    elif mime_type.startswith("text/"):
        return "code"
    elif mime_type in ["application/zip", "application/x-rar-compressed", "application/x-tar", "application/gzip", "application/x-7z-compressed"]:
        return "archive"
    else:
        return "file"



@router.get("/{workspace_id}", response_model=list[AssetRead])
def list_assets(workspace_id: str, db: Session = Depends(get_db)):
    """List all assets in a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return db.query(Asset).filter(Asset.workspace_id == workspace_id).all()


@router.get("/asset/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    """Get a specific asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/asset/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: str, db: Session = Depends(get_db)):
    """Delete an asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return None
