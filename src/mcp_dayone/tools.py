"""Day One CLI operations and tools."""

import subprocess
import json
import os
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import shlex


class DayOneError(Exception):
    """Exception raised for Day One CLI errors."""
    pass


class DayOneTools:
    """Wrapper for Day One CLI operations."""
    
    def __init__(self, cli_path: str = "dayone2"):
        self.cli_path = cli_path
        self._verify_cli()
        self.db_path = self._get_db_path()
    
    def _verify_cli(self) -> None:
        """Verify Day One CLI is available."""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise DayOneError(
                f"Day One CLI '{self.cli_path}' not found or not working. "
                f"Please install Day One CLI first. Error: {e}"
            )
    
    def _get_db_path(self) -> Path:
        """Get the path to Day One database."""
        db_path = Path.home() / "Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOneDB2.sqlite"
        return db_path
    
    def _get_db_connection(self) -> sqlite3.Connection:
        """Get a connection to the Day One database."""
        if not self.db_path.exists():
            raise DayOneError(
                f"Day One database not found at {self.db_path}. "
                "Make sure Day One app is installed and has been run at least once."
            )
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except sqlite3.Error as e:
            raise DayOneError(f"Failed to connect to Day One database: {e}")
    
    def create_entry(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        date: Optional[str] = None,
        journal: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        starred: Optional[bool] = None,
        coordinates: Optional[Dict[str, float]] = None,
        timezone: Optional[str] = None,
        all_day: Optional[bool] = None
    ) -> str:
        """Create a new Day One journal entry.
        
        Args:
            content: The entry text content
            tags: Optional list of tags to add
            date: Optional date string (YYYY-MM-DD HH:MM:SS format)
            journal: Optional journal name
            attachments: Optional list of file paths to attach (up to 10)
            starred: Optional flag to mark entry as starred
            coordinates: Optional dict with 'latitude' and 'longitude' keys
            timezone: Optional timezone string
            all_day: Optional flag to mark as all-day event
            
        Returns:
            UUID of the created entry
            
        Raises:
            DayOneError: If entry creation fails
        """
        if not content.strip():
            raise DayOneError("Entry content cannot be empty")
        
        # Validate attachments
        if attachments:
            if len(attachments) > 10:
                raise DayOneError("Maximum 10 attachments allowed per entry")
            
            for attachment in attachments:
                if not os.path.exists(attachment):
                    raise DayOneError(f"Attachment file not found: {attachment}")
        
        # Validate coordinates
        if coordinates:
            if 'latitude' not in coordinates or 'longitude' not in coordinates:
                raise DayOneError("Coordinates must include both 'latitude' and 'longitude'")
        
        # Build command
        cmd = [self.cli_path]
        
        # Add attachments
        if attachments:
            cmd.extend(["--attachments"] + attachments)
        
        # Add tags
        if tags:
            cmd.extend(["--tags"] + tags)
        
        # Add journal
        if journal:
            cmd.extend(["--journal", journal])
        
        # Add date
        if date:
            cmd.extend(["--date", date])
        
        # Add starred flag
        if starred:
            cmd.append("--starred")
        
        # Add coordinates
        if coordinates:
            coord_str = f"{coordinates['latitude']} {coordinates['longitude']}"
            cmd.extend(["--coordinate", coord_str])
        
        # Add timezone
        if timezone:
            cmd.extend(["--time-zone", timezone])
        
        # Add all-day flag
        if all_day:
            cmd.append("--all-day")
        
        # Add the command and content
        cmd.extend(["new", content])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract UUID from output
            output = result.stdout.strip()
            if "Created new entry with uuid:" in output:
                uuid = output.split("uuid:")[-1].strip()
                return uuid
            else:
                return output
                
        except subprocess.CalledProcessError as e:
            raise DayOneError(f"Failed to create entry: {e.stderr}")
    
    def list_journals(self) -> List[str]:
        """List available journals.
        
        Note: Day One CLI doesn't provide a direct way to list journals.
        This method returns a helpful message explaining the limitation.
        
        Returns:
            List with explanatory message
            
        Raises:
            DayOneError: If there's an issue
        """
        # Day One CLI doesn't have a journals command
        return [
            "Day One CLI doesn't provide a command to list journals.",
            "You can specify a journal name using the --journal parameter when creating entries.",
            "If no journal is specified, entries go to the default journal."
        ]
    
    def get_entry_count(self, journal: Optional[str] = None) -> int:
        """Get total number of entries.
        
        Note: Day One CLI doesn't provide a command to count entries.
        
        Args:
            journal: Optional journal name to count entries for
            
        Returns:
            Always returns -1 to indicate this functionality is not available
            
        Raises:
            DayOneError: If there's an issue
        """
        # Day One CLI doesn't have a list command
        raise DayOneError(
            "Day One CLI doesn't provide a command to count entries. "
            "You can view entry counts through the Day One app interface."
        )
    
    def read_recent_entries(self, limit: int = 10, journal: Optional[str] = None) -> List[Dict[str, Any]]:
        """Read recent journal entries from the database.
        
        Args:
            limit: Maximum number of entries to return
            journal: Optional journal name to filter by
            
        Returns:
            List of entry dictionaries with metadata
            
        Raises:
            DayOneError: If database access fails
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Base query to get entries with journal information
            query = """
            SELECT 
                e.uuid,
                e.text,
                e.creationDate,
                e.modifiedDate,
                e.starred,
                e.timeZone,
                j.name as journal_name,
                e.location,
                e.weather
            FROM ZENTRY e
            LEFT JOIN ZJOURNAL j ON e.journal = j.Z_PK
            """
            
            params = []
            if journal:
                query += " WHERE j.name = ?"
                params.append(journal)
            
            query += " ORDER BY e.creationDate DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            entries = []
            
            for row in cursor.fetchall():
                entry = {
                    'uuid': row['uuid'],
                    'text': row['text'] or '',
                    'creation_date': datetime.fromtimestamp(row['creationDate'] + 978307200) if row['creationDate'] else None,  # Convert from Core Data timestamp
                    'modified_date': datetime.fromtimestamp(row['modifiedDate'] + 978307200) if row['modifiedDate'] else None,
                    'starred': bool(row['starred']),
                    'timezone': row['timeZone'],
                    'journal_name': row['journal_name'] or 'Default',
                    'has_location': bool(row['location']),
                    'has_weather': bool(row['weather'])
                }
                
                # Get tags for this entry
                entry['tags'] = self._get_entry_tags(cursor, row['uuid'])
                
                entries.append(entry)
            
            conn.close()
            return entries
            
        except sqlite3.Error as e:
            raise DayOneError(f"Failed to read entries from database: {e}")
    
    def _get_entry_tags(self, cursor: sqlite3.Cursor, entry_uuid: str) -> List[str]:
        """Get tags for a specific entry."""
        try:
            cursor.execute("""
                SELECT t.name 
                FROM ZTAG t
                JOIN Z_5TAGS zt ON t.Z_PK = zt.Z_10TAGS
                JOIN ZENTRY e ON zt.Z_5ENTRIES = e.Z_PK
                WHERE e.uuid = ?
            """, (entry_uuid,))
            
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def search_entries(self, search_text: str, limit: int = 20, journal: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search journal entries by text content.
        
        Args:
            search_text: Text to search for in entry content
            limit: Maximum number of entries to return
            journal: Optional journal name to filter by
            
        Returns:
            List of entry dictionaries matching the search
            
        Raises:
            DayOneError: If database access fails
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                e.uuid,
                e.text,
                e.creationDate,
                e.modifiedDate,
                e.starred,
                e.timeZone,
                j.name as journal_name
            FROM ZENTRY e
            LEFT JOIN ZJOURNAL j ON e.journal = j.Z_PK
            WHERE e.text LIKE ?
            """
            
            params = [f'%{search_text}%']
            
            if journal:
                query += " AND j.name = ?"
                params.append(journal)
            
            query += " ORDER BY e.creationDate DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            entries = []
            
            for row in cursor.fetchall():
                entry = {
                    'uuid': row['uuid'],
                    'text': row['text'] or '',
                    'creation_date': datetime.fromtimestamp(row['creationDate'] + 978307200) if row['creationDate'] else None,
                    'modified_date': datetime.fromtimestamp(row['modifiedDate'] + 978307200) if row['modifiedDate'] else None,
                    'starred': bool(row['starred']),
                    'timezone': row['timeZone'],
                    'journal_name': row['journal_name'] or 'Default'
                }
                
                entry['tags'] = self._get_entry_tags(cursor, row['uuid'])
                entries.append(entry)
            
            conn.close()
            return entries
            
        except sqlite3.Error as e:
            raise DayOneError(f"Failed to search entries: {e}")
    
    def list_journals_from_db(self) -> List[Dict[str, Any]]:
        """List all journals from the database with entry counts.
        
        Returns:
            List of journal dictionaries with metadata
            
        Raises:
            DayOneError: If database access fails
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    j.name,
                    j.uuid,
                    COUNT(e.Z_PK) as entry_count,
                    MAX(e.creationDate) as last_entry_date
                FROM ZJOURNAL j
                LEFT JOIN ZENTRY e ON e.journal = j.Z_PK
                GROUP BY j.Z_PK, j.name, j.uuid
                ORDER BY j.name
            """)
            
            journals = []
            for row in cursor.fetchall():
                journal = {
                    'name': row['name'],
                    'uuid': row['uuid'],
                    'entry_count': row['entry_count'],
                    'last_entry_date': datetime.fromtimestamp(row['last_entry_date'] + 978307200) if row['last_entry_date'] else None
                }
                journals.append(journal)
            
            conn.close()
            return journals
            
        except sqlite3.Error as e:
            raise DayOneError(f"Failed to list journals from database: {e}")
    
    def get_entry_count_from_db(self, journal: Optional[str] = None) -> int:
        """Get actual entry count from database.
        
        Args:
            journal: Optional journal name to count entries for
            
        Returns:
            Number of entries
            
        Raises:
            DayOneError: If database access fails
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            if journal:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM ZENTRY e
                    JOIN ZJOURNAL j ON e.journal = j.Z_PK
                    WHERE j.name = ?
                """, (journal,))
            else:
                cursor.execute("SELECT COUNT(*) FROM ZENTRY")
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
            
        except sqlite3.Error as e:
            raise DayOneError(f"Failed to count entries from database: {e}")