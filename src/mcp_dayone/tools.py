"""Day One CLI operations and tools."""

import subprocess
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import shlex


class DayOneError(Exception):
    """Exception raised for Day One CLI errors."""
    pass


class DayOneTools:
    """Wrapper for Day One CLI operations."""
    
    def __init__(self, cli_path: str = "dayone2"):
        self.cli_path = cli_path
        self._verify_cli()
    
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
        cmd = [self.cli_path, "new"]
        
        # Add content (properly escaped)
        cmd.append(content)
        
        # Add tags
        if tags:
            for tag in tags:
                cmd.append(f"#{tag}")
        
        # Add date
        if date:
            cmd.extend(["--date", date])
        
        # Add journal
        if journal:
            cmd.extend(["--journal", journal])
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                cmd.extend(["--attachments", attachment])
        
        # Add starred flag
        if starred:
            cmd.append("--starred")
        
        # Add coordinates
        if coordinates:
            coord_str = f"{coordinates['latitude']},{coordinates['longitude']}"
            cmd.extend(["--coordinate", coord_str])
        
        # Add timezone
        if timezone:
            cmd.extend(["--time-zone", timezone])
        
        # Add all-day flag
        if all_day:
            cmd.append("--all-day")
        
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
        
        Returns:
            List of journal names
            
        Raises:
            DayOneError: If listing fails
        """
        try:
            result = subprocess.run(
                [self.cli_path, "journals"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse journal names from output
            journals = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    journals.append(line.strip())
            
            return journals
            
        except subprocess.CalledProcessError as e:
            raise DayOneError(f"Failed to list journals: {e.stderr}")
    
    def get_entry_count(self, journal: Optional[str] = None) -> int:
        """Get total number of entries.
        
        Args:
            journal: Optional journal name to count entries for
            
        Returns:
            Number of entries
            
        Raises:
            DayOneError: If count fails
        """
        cmd = [self.cli_path, "list"]
        
        if journal:
            cmd.extend(["--journal", journal])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Count non-empty lines
            lines = [line for line in result.stdout.strip().split('\n') if line.strip()]
            return len(lines)
            
        except subprocess.CalledProcessError as e:
            raise DayOneError(f"Failed to count entries: {e.stderr}")