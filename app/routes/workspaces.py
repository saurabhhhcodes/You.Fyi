from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Workspace, Kit, Asset
from app.schemas import WorkspaceCreate, WorkspaceRead, WorkspaceMerge

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def create_workspace(workspace: WorkspaceCreate, db: Session = Depends(get_db)):
    """Create a new workspace"""
    db_workspace = Workspace(**workspace.model_dump())
    db.add(db_workspace)
    try:
        db.commit()
        db.refresh(db_workspace)
        return db_workspace
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[WorkspaceRead])
def list_workspaces(db: Session = Depends(get_db)):
    """List all workspaces"""
    return db.query(Workspace).all()


@router.get("/{workspace_id}", response_model=WorkspaceRead)
def get_workspace(workspace_id: str, db: Session = Depends(get_db)):
    """Get a specific workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(workspace_id: str, db: Session = Depends(get_db)):
    """Delete a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    db.delete(workspace)
    db.commit()
    return None


@router.post("/merge", status_code=status.HTTP_200_OK)
def merge_workspaces(data: WorkspaceMerge, db: Session = Depends(get_db)):
    """
    Merge source workspace into target workspace.
    1. Move all assets from source to target.
    2. Move all kits from source to target.
    3. Delete source workspace.
    """
    source = db.query(Workspace).filter(Workspace.id == data.source_id).first()
    target = db.query(Workspace).filter(Workspace.id == data.target_id).first()

    if not source or not target:
        raise HTTPException(status_code=404, detail="Source or target workspace not found")

    # Move Assets
    for asset in source.assets:
        asset.workspace_id = target.id
    
    # Move Kits
    for kit in source.kits:
        kit.workspace_id = target.id

    db.commit()

    # Delete Source
    db.delete(source)
    db.commit()

    return {"message": "Workspaces merged successfully"}

@router.get("/{workspace_id}/shared-links")
def get_all_shared_links(workspace_id: str, db: Session = Depends(get_db)):
    """Get all shared links for a workspace (workspace links + kit links)"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Workspace Links
    from app.models import WorkspaceSharingLink, SharingLink
    ws_links = db.query(WorkspaceSharingLink).filter(WorkspaceSharingLink.workspace_id == workspace_id).all()
    
    # Kit Links
    kit_links_data = []
    for kit in workspace.kits:
        links = db.query(SharingLink).filter(SharingLink.kit_id == kit.id).all()
        if links:
            kit_links_data.append({
                "kit_id": kit.id,
                "kit_name": kit.name,
                "links": links
            })

    return {
        "workspace_links": ws_links,
        "kit_links": kit_links_data
    }
