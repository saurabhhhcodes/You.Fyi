from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import SharingLink, Kit, Workspace, WorkspaceSharingLink
from app.schemas import SharingLinkCreate, SharingLinkRead, WorkspaceSharingLinkRead, AssetRead
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/sharing-links", tags=["sharing-links"])


def generate_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


@router.post("/kit/{kit_id}", response_model=SharingLinkRead, status_code=status.HTTP_201_CREATED)
def create_sharing_link(kit_id: str, link_data: SharingLinkCreate, db: Session = Depends(get_db)):
    """Create a shareable link for a kit"""
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    expires_at = None
    if link_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=link_data.expires_in_days)
    
    db_link = SharingLink(
        kit_id=kit_id,
        token=generate_token(),
        expires_at=expires_at
    )
    
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


from typing import Union

@router.get("/token/{token}", response_model=Union[SharingLinkRead, WorkspaceSharingLinkRead])
def get_sharing_link_by_token(token: str, db: Session = Depends(get_db)):
    """Get sharing link details by token"""
    # Try Kit Link
    link = db.query(SharingLink).filter(SharingLink.token == token).first()
    if link:
        # Check if link is still active
        if not link.is_active:
            raise HTTPException(status_code=403, detail="Sharing link is inactive")
        
        if link.expires_at and link.expires_at < datetime.utcnow():
            raise HTTPException(status_code=403, detail="Sharing link has expired")
        return link

    # Try Workspace Link
    ws_link = db.query(WorkspaceSharingLink).filter(WorkspaceSharingLink.token == token).first()
    if ws_link:
        if not ws_link.is_active:
            raise HTTPException(status_code=403, detail="Sharing link is inactive")
        
        if ws_link.expires_at and ws_link.expires_at < datetime.utcnow():
            raise HTTPException(status_code=403, detail="Sharing link has expired")
        return ws_link

    raise HTTPException(status_code=404, detail="Sharing link not found")


@router.get("/kit/{kit_id}", response_model=list[SharingLinkRead])
def list_sharing_links(kit_id: str, db: Session = Depends(get_db)):
    """List all sharing links for a kit"""
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    return db.query(SharingLink).filter(SharingLink.kit_id == kit_id).all()


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sharing_link(link_id: str, db: Session = Depends(get_db)):
    """Delete a sharing link"""
    link = db.query(SharingLink).filter(SharingLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Sharing link not found")
    
    db.delete(link)
    db.commit()
    return None


@router.patch("/{link_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_sharing_link(link_id: str, db: Session = Depends(get_db)):
    """Deactivate a sharing link"""
    link = db.query(SharingLink).filter(SharingLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Sharing link not found")
    
    link.is_active = False
    db.commit()
    db.refresh(link)
    return link


@router.delete("/workspace/link/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace_sharing_link(link_id: str, db: Session = Depends(get_db)):
    """Delete a workspace sharing link"""
    link = db.query(WorkspaceSharingLink).filter(WorkspaceSharingLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Sharing link not found")
    
    db.delete(link)
    db.commit()
    return None


@router.patch("/workspace/link/{link_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_workspace_sharing_link(link_id: str, db: Session = Depends(get_db)):
    """Deactivate a workspace sharing link"""
    link = db.query(WorkspaceSharingLink).filter(WorkspaceSharingLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Sharing link not found")
    
    link.is_active = False
    db.commit()
    db.refresh(link)
    return link


@router.post("/workspace/{workspace_id}", response_model=WorkspaceSharingLinkRead, status_code=status.HTTP_201_CREATED)
def create_workspace_sharing_link(workspace_id: str, link_data: SharingLinkCreate, db: Session = Depends(get_db)):
    """Create a shareable link for a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    expires_at = None
    if link_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=link_data.expires_in_days)
    
    db_link = WorkspaceSharingLink(
        workspace_id=workspace_id,
        token=generate_token(),
        expires_at=expires_at
    )
    
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


@router.get("/workspace/{workspace_id}", response_model=list[WorkspaceSharingLinkRead])
def list_workspace_sharing_links(workspace_id: str, db: Session = Depends(get_db)):
    """List all sharing links for a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return db.query(WorkspaceSharingLink).filter(WorkspaceSharingLink.workspace_id == workspace_id).all()


@router.get("/token/{token}/assets", response_model=list[AssetRead])
def list_sharing_link_assets(token: str, db: Session = Depends(get_db)):
    """List assets accessible via a sharing link"""
    # Try Kit Link
    link = db.query(SharingLink).filter(SharingLink.token == token).first()
    if link:
        if not link.is_active:
            raise HTTPException(status_code=403, detail="Sharing link is inactive")
        if link.expires_at and link.expires_at < datetime.utcnow():
            raise HTTPException(status_code=403, detail="Sharing link has expired")
        
        kit = db.query(Kit).filter(Kit.id == link.kit_id).first()
        if not kit:
            raise HTTPException(status_code=404, detail="Kit not found")
        return kit.assets

    # Try Workspace Link
    ws_link = db.query(WorkspaceSharingLink).filter(WorkspaceSharingLink.token == token).first()
    if ws_link:
        if not ws_link.is_active:
            raise HTTPException(status_code=403, detail="Sharing link is inactive")
        if ws_link.expires_at and ws_link.expires_at < datetime.utcnow():
            raise HTTPException(status_code=403, detail="Sharing link has expired")
        
        return db.query(Asset).filter(Asset.workspace_id == ws_link.workspace_id).all()

    raise HTTPException(status_code=404, detail="Sharing link not found")
