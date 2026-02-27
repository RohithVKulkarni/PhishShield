"""
User List Service

Handles whitelist and blacklist management for PhishShield.

Features:
- Add/remove URLs from whitelist or blacklist
- Check if URL matches any list entries
- Support for domain patterns and wildcards
- Import/export functionality
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.core.models import UserList, ListType
from urllib.parse import urlparse
import fnmatch
import json


class UserListService:
    """Service for managing user whitelists and blacklists"""
    
    @staticmethod
    def add_to_list(
        db: Session,
        list_type: ListType,
        pattern: str,
        note: Optional[str] = None
    ) -> UserList:
        """
        Add a URL or domain pattern to a list.
        
        Args:
            db: Database session
            list_type: "whitelist" or "blacklist"
            pattern: URL or domain pattern (e.g., "example.com", "*.example.com")
            note: Optional user note
            
        Returns:
            Created UserList entry
        """
        # Normalize pattern (extract domain if full URL provided)
        normalized_pattern = UserListService._normalize_pattern(pattern)
        
        # Check if pattern already exists
        existing = db.query(UserList).filter(
            UserList.list_type == list_type,
            UserList.pattern == normalized_pattern
        ).first()
        
        if existing:
            # Update note if provided
            if note:
                existing.note = note
                db.commit()
                db.refresh(existing)
            return existing
        
        # Create new entry
        entry = UserList(
            list_type=list_type,
            pattern=normalized_pattern,
            note=note
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        return entry
    
    @staticmethod
    def remove_from_list(db: Session, entry_id: int) -> bool:
        """
        Remove an entry from a list.
        
        Args:
            db: Database session
            entry_id: ID of the entry to remove
            
        Returns:
            True if removed, False if not found
        """
        entry = db.query(UserList).filter(UserList.id == entry_id).first()
        if entry:
            db.delete(entry)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_all_lists(db: Session) -> Dict[str, List[UserList]]:
        """
        Get all whitelist and blacklist entries.
        
        Returns:
            Dictionary with "whitelist" and "blacklist" keys
        """
        whitelist = db.query(UserList).filter(
            UserList.list_type == ListType.WHITELIST
        ).order_by(UserList.created_at.desc()).all()
        
        blacklist = db.query(UserList).filter(
            UserList.list_type == ListType.BLACKLIST
        ).order_by(UserList.created_at.desc()).all()
        
        return {
            "whitelist": whitelist,
            "blacklist": blacklist
        }
    
    @staticmethod
    def check_url(db: Session, url: str) -> Optional[Dict]:
        """
        Check if a URL matches any whitelist or blacklist entry.
        
        Args:
            db: Database session
            url: URL to check
            
        Returns:
            Dictionary with match info if found, None otherwise:
            {
                "list_type": "whitelist" or "blacklist",
                "pattern": "matched pattern",
                "note": "user note",
                "entry_id": 123
            }
        """
        # Extract domain from URL
        domain = UserListService._extract_domain(url)
        
        # Check blacklist first (higher priority)
        blacklist = db.query(UserList).filter(
            UserList.list_type == ListType.BLACKLIST
        ).all()
        
        for entry in blacklist:
            if UserListService._matches_pattern(url, domain, entry.pattern):
                return {
                    "list_type": "blacklist",
                    "pattern": entry.pattern,
                    "note": entry.note,
                    "entry_id": entry.id
                }
        
        # Check whitelist
        whitelist = db.query(UserList).filter(
            UserList.list_type == ListType.WHITELIST
        ).all()
        
        for entry in whitelist:
            if UserListService._matches_pattern(url, domain, entry.pattern):
                return {
                    "list_type": "whitelist",
                    "pattern": entry.pattern,
                    "note": entry.note,
                    "entry_id": entry.id
                }
        
        return None
    
    @staticmethod
    def export_lists(db: Session, format: str = "json") -> str:
        """
        Export all lists to JSON or CSV format.
        
        Args:
            db: Database session
            format: "json" or "csv"
            
        Returns:
            Formatted string
        """
        lists = UserListService.get_all_lists(db)
        
        if format == "json":
            export_data = {
                "whitelist": [
                    {"pattern": e.pattern, "note": e.note}
                    for e in lists["whitelist"]
                ],
                "blacklist": [
                    {"pattern": e.pattern, "note": e.note}
                    for e in lists["blacklist"]
                ]
            }
            return json.dumps(export_data, indent=2)
        
        elif format == "csv":
            lines = ["list_type,pattern,note"]
            for entry in lists["whitelist"]:
                lines.append(f'whitelist,"{entry.pattern}","{entry.note or ""}"')
            for entry in lists["blacklist"]:
                lines.append(f'blacklist,"{entry.pattern}","{entry.note or ""}"')
            return "\n".join(lines)
        
        raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def import_lists(db: Session, data: str, format: str = "json") -> Dict:
        """
        Import lists from JSON or CSV format.
        
        Args:
            db: Database session
            data: Import data string
            format: "json" or "csv"
            
        Returns:
            Import statistics
        """
        imported = {"whitelist": 0, "blacklist": 0}
        
        if format == "json":
            import_data = json.loads(data)
            
            for entry in import_data.get("whitelist", []):
                UserListService.add_to_list(
                    db, ListType.WHITELIST, entry["pattern"], entry.get("note")
                )
                imported["whitelist"] += 1
            
            for entry in import_data.get("blacklist", []):
                UserListService.add_to_list(
                    db, ListType.BLACKLIST, entry["pattern"], entry.get("note")
                )
                imported["blacklist"] += 1
        
        elif format == "csv":
            lines = data.strip().split("\n")[1:]  # Skip header
            for line in lines:
                parts = line.split(",")
                if len(parts) >= 2:
                    list_type = ListType(parts[0].strip())
                    pattern = parts[1].strip().strip('"')
                    note = parts[2].strip().strip('"') if len(parts) > 2 else None
                    
                    UserListService.add_to_list(db, list_type, pattern, note)
                    imported[list_type.value] += 1
        
        return imported
    
    # Helper methods
    
    @staticmethod
    def _normalize_pattern(pattern: str) -> str:
        """Normalize a pattern by extracting domain if full URL provided"""
        if pattern.startswith("http://") or pattern.startswith("https://"):
            return UserListService._extract_domain(pattern)
        return pattern.lower().strip()
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower() if parsed.netloc else url.lower()
        except:
            return url.lower()
    
    @staticmethod
    def _matches_pattern(url: str, domain: str, pattern: str) -> bool:
        """
        Check if URL/domain matches a pattern.
        
        Supports:
        - Exact domain match: "example.com"
        - Wildcard subdomain: "*.example.com"
        - Full URL match: "http://example.com/specific-page"
        """
        pattern = pattern.lower()
        
        # Exact domain match
        if domain == pattern:
            return True
        
        # Wildcard pattern match
        if "*" in pattern:
            if fnmatch.fnmatch(domain, pattern):
                return True
            if fnmatch.fnmatch(url.lower(), pattern):
                return True
        
        # Subdomain match (pattern "example.com" matches "sub.example.com")
        if domain.endswith("." + pattern):
            return True
        
        # Full URL match
        if url.lower().startswith(pattern):
            return True
        
        return False
