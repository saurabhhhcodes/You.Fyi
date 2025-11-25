from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class WorkspaceRead(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    asset_type: str = "document"


class AssetUpload(BaseModel):
    """Schema for file uploads"""
    name: str
    description: Optional[str] = None
    asset_type: str = "file"  # Will be determined from mime type


class AssetRead(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    content: str
    asset_type: str
    mime_type: Optional[str]
    file_size: Optional[int]
    file_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    asset_ids: Optional[List[str]] = []


class KitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    asset_ids: Optional[List[str]] = None


class KitRead(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    assets: List[AssetRead]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SharingLinkCreate(BaseModel):
    expires_in_days: Optional[int] = None


class SharingLinkRead(BaseModel):
    id: str
    kit_id: str
    token: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class RagQueryRequest(BaseModel):
    query: str
    kit_id: Optional[str] = None
    use_llm: bool = True
    model: Optional[str] = None


class RagQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    model: str
