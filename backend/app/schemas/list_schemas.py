"""
Pydantic Schemas for User List Management

Request and response models for whitelist/blacklist API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ListTypeEnum(str, Enum):
    """List type enumeration"""
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"


class UserListCreate(BaseModel):
    """Request model for creating a list entry"""
    list_type: ListTypeEnum
    pattern: str = Field(..., min_length=1, max_length=500, description="URL or domain pattern")
    note: Optional[str] = Field(None, max_length=1000, description="Optional note")
    
    @validator('pattern')
    def validate_pattern(cls, v):
        """Ensure pattern is not empty after stripping"""
        if not v.strip():
            raise ValueError("Pattern cannot be empty")
        return v.strip()


class UserListResponse(BaseModel):
    """Response model for a list entry"""
    id: int
    list_type: str
    pattern: str
    note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserListUpdate(BaseModel):
    """Request model for updating a list entry"""
    note: Optional[str] = Field(None, max_length=1000)


class UserListsResponse(BaseModel):
    """Response model for all lists"""
    whitelist: List[UserListResponse]
    blacklist: List[UserListResponse]


class UserListCheckResponse(BaseModel):
    """Response model for URL check"""
    matched: bool
    list_type: Optional[str] = None
    pattern: Optional[str] = None
    note: Optional[str] = None
    entry_id: Optional[int] = None


class ImportRequest(BaseModel):
    """Request model for importing lists"""
    data: str = Field(..., description="JSON or CSV data to import")
    format: str = Field("json", description="Format: 'json' or 'csv'")
    
    @validator('format')
    def validate_format(cls, v):
        if v not in ["json", "csv"]:
            raise ValueError("Format must be 'json' or 'csv'")
        return v


class ImportResponse(BaseModel):
    """Response model for import operation"""
    success: bool
    imported: dict
    message: str


class ExportResponse(BaseModel):
    """Response model for export operation"""
    data: str
    format: str
