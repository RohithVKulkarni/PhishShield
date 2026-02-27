"""
User Lists API Endpoints

Provides REST API for whitelist and blacklist management.

Endpoints:
    POST /api/v1/lists - Add entry to whitelist or blacklist
    GET /api/v1/lists - Get all lists
    DELETE /api/v1/lists/{entry_id} - Remove entry
    PUT /api/v1/lists/{entry_id} - Update entry
    POST /api/v1/lists/check - Check if URL is in any list
    POST /api/v1/lists/import - Import lists from JSON/CSV
    GET /api/v1/lists/export - Export lists to JSON/CSV
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.list_schemas import (
    UserListCreate,
    UserListResponse,
    UserListUpdate,
    UserListsResponse,
    UserListCheckResponse,
    ImportRequest,
    ImportResponse,
    ExportResponse
)
from app.services.user_list_service import UserListService
from app.core.models import ListType

router = APIRouter()


@router.post("/lists", response_model=UserListResponse, status_code=201)
async def add_to_list(
    request: UserListCreate,
    db: Session = Depends(get_db)
):
    """
    Add a URL or domain pattern to whitelist or blacklist.
    
    Example:
        POST /api/v1/lists
        {
            "list_type": "whitelist",
            "pattern": "example.com",
            "note": "Trusted site"
        }
    """
    try:
        entry = UserListService.add_to_list(
            db=db,
            list_type=ListType(request.list_type),
            pattern=request.pattern,
            note=request.note
        )
        return entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to list: {str(e)}")


@router.get("/lists", response_model=UserListsResponse)
async def get_all_lists(db: Session = Depends(get_db)):
    """
    Get all whitelist and blacklist entries.
    
    Returns:
        {
            "whitelist": [...],
            "blacklist": [...]
        }
    """
    try:
        lists = UserListService.get_all_lists(db)
        return lists
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving lists: {str(e)}")


@router.delete("/lists/{entry_id}")
async def remove_from_list(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove an entry from a list.
    
    Args:
        entry_id: ID of the entry to remove
    """
    try:
        removed = UserListService.remove_from_list(db, entry_id)
        if not removed:
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"success": True, "message": "Entry removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing entry: {str(e)}")


@router.put("/lists/{entry_id}", response_model=UserListResponse)
async def update_list_entry(
    entry_id: int,
    request: UserListUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an entry's note.
    
    Args:
        entry_id: ID of the entry to update
        request: Update data (currently only note)
    """
    try:
        from app.core.models import UserList
        
        entry = db.query(UserList).filter(UserList.id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        if request.note is not None:
            entry.note = request.note
            db.commit()
            db.refresh(entry)
        
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating entry: {str(e)}")


@router.post("/lists/check", response_model=UserListCheckResponse)
async def check_url(
    url: str = Query(..., description="URL to check"),
    db: Session = Depends(get_db)
):
    """
    Check if a URL matches any whitelist or blacklist entry.
    
    Example:
        POST /api/v1/lists/check?url=http://example.com
    
    Returns:
        {
            "matched": true,
            "list_type": "whitelist",
            "pattern": "example.com",
            "note": "Trusted site",
            "entry_id": 123
        }
    """
    try:
        result = UserListService.check_url(db, url)
        
        if result:
            return {
                "matched": True,
                **result
            }
        else:
            return {
                "matched": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking URL: {str(e)}")


@router.post("/lists/import", response_model=ImportResponse)
async def import_lists(
    request: ImportRequest,
    db: Session = Depends(get_db)
):
    """
    Import lists from JSON or CSV format.
    
    JSON format:
        {
            "whitelist": [
                {"pattern": "example.com", "note": "Trusted"}
            ],
            "blacklist": [
                {"pattern": "evil.com", "note": "Phishing"}
            ]
        }
    
    CSV format:
        list_type,pattern,note
        whitelist,"example.com","Trusted"
        blacklist,"evil.com","Phishing"
    """
    try:
        imported = UserListService.import_lists(db, request.data, request.format)
        return {
            "success": True,
            "imported": imported,
            "message": f"Imported {sum(imported.values())} entries"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.get("/lists/export", response_model=ExportResponse)
async def export_lists(
    format: str = Query("json", description="Export format: 'json' or 'csv'"),
    db: Session = Depends(get_db)
):
    """
    Export all lists to JSON or CSV format.
    
    Args:
        format: "json" or "csv"
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
        
        data = UserListService.export_lists(db, format)
        return {
            "data": data,
            "format": format
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
