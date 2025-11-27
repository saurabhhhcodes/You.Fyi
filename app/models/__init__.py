from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


# Association table for many-to-many relationship between Assets and Kits
asset_kit_association = Table(
    'asset_kit',
    Base.metadata,
    Column('asset_id', String, ForeignKey('assets.id')),
    Column('kit_id', String, ForeignKey('kits.id'))
)


class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assets = relationship("Asset", back_populates="workspace", cascade="all, delete-orphan")
    kits = relationship("Kit", back_populates="workspace", cascade="all, delete-orphan")
    sharing_links = relationship("WorkspaceSharingLink", back_populates="workspace", cascade="all, delete-orphan")


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text)  # File content or data (base64 for binary files)
    asset_type = Column(String)  # e.g., "document", "image", "video", "executable", "data"
    mime_type = Column(String, nullable=True)  # e.g., "image/png", "application/pdf", "video/mp4"
    file_size = Column(Integer, nullable=True)  # File size in bytes
    file_path = Column(String, nullable=True)  # Original file path or name
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="assets")
    kits = relationship("Kit", secondary=asset_kit_association, back_populates="assets")


class Kit(Base):
    __tablename__ = "kits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="kits")
    assets = relationship("Asset", secondary=asset_kit_association, back_populates="kits")
    sharing_links = relationship("SharingLink", back_populates="kit", cascade="all, delete-orphan")


class SharingLink(Base):
    __tablename__ = "sharing_links"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kit_id = Column(String, ForeignKey("kits.id"), nullable=False)
    token = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    kit = relationship("Kit", back_populates="sharing_links")


class WorkspaceSharingLink(Base):
    __tablename__ = "workspace_sharing_links"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    token = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="sharing_links")
