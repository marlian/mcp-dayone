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