from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Kit, Asset, Workspace
from app.schemas import KitCreate, KitUpdate, KitRead

router = APIRouter(prefix="/kits", tags=["kits"])


@router.post("/{workspace_id}", response_model=KitRead, status_code=status.HTTP_201_CREATED)
def create_kit(workspace_id: str, kit: KitCreate, db: Session = Depends(get_db)):
    """Create a new kit in a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    db_kit = Kit(workspace_id=workspace_id, name=kit.name, description=kit.description)
    
    # Add assets if provided
    if kit.asset_ids:
        assets = db.query(Asset).filter(Asset.id.in_(kit.asset_ids)).all()
        db_kit.assets = assets
    
    db.add(db_kit)
    db.commit()
    db.refresh(db_kit)
    return db_kit


@router.get("/{workspace_id}", response_model=list[KitRead])
def list_kits(workspace_id: str, db: Session = Depends(get_db)):
    """List all kits in a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return db.query(Kit).filter(Kit.workspace_id == workspace_id).all()


@router.get("/kit/{kit_id}", response_model=KitRead)
def get_kit(kit_id: str, db: Session = Depends(get_db)):
    """Get a specific kit"""
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    return kit


@router.put("/kit/{kit_id}", response_model=KitRead)
def update_kit(kit_id: str, kit_update: KitUpdate, db: Session = Depends(get_db)):
    """Update a kit"""
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    if kit_update.name:
        kit.name = kit_update.name
    if kit_update.description:
        kit.description = kit_update.description
    if kit_update.asset_ids is not None:
        assets = db.query(Asset).filter(Asset.id.in_(kit_update.asset_ids)).all()
        kit.assets = assets
    
    db.commit()
    db.refresh(kit)
    return kit


@router.delete("/kit/{kit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kit(kit_id: str, db: Session = Depends(get_db)):
    """Delete a kit"""
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    db.delete(kit)
    db.commit()
    return None
