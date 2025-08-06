"""MCP server for Day One Journal integration."""

import asyncio
import logging
import json
import datetime
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    ServerCapabilities,
    TextContent,
    Tool,
    ToolsCapability,
)
from pydantic import BaseModel, Field

from .tools import DayOneTools, DayOneError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔍 REQUEST LOGGER - Debug MCP communication
def log_mcp_request(request_data, source="unknown"):
    """Log all MCP requests to file for debugging."""
    log_dir = Path(__file__).parent.parent.parent / "mcp_request_logs"
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().isoformat()
    log_file = log_dir / f"dayone_requests_{datetime.datetime.now().strftime('%Y%m%d')}.log"
    
    log_entry = {
        "timestamp": timestamp,
        "source": source,
        "request": request_data
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, indent=2, ensure_ascii=False) + "\n" + "="*80 + "\n")
    
    logger.info(f"🔍 [DEBUG] Logged request from {source} to {log_file}")

# Tool argument models
class CreateEntryArgs(BaseModel):
    content: str = Field(description="The text content of the journal entry")
    tags: list[str] = Field(default=[], description="Optional list of tags for the entry")
    date: str = Field(default="", description="Optional date in YYYY-MM-DD HH:MM:SS format")
    journal: str = Field(default="", description="Optional journal name")
    attachments: list[str] = Field(default=[], description="Optional list of file paths to attach (max 10)")
    starred: bool = Field(default=False, description="Mark entry as starred/important")
    coordinates: dict[str, float] = Field(default={}, description="Optional coordinates with 'latitude' and 'longitude' keys")
    timezone: str = Field(default="", description="Optional timezone (e.g., 'America/New_York')")
    all_day: bool = Field(default=False, description="Mark as all-day event")

class ListJournalsArgs(BaseModel):
    pass

class GetEntryCountArgs(BaseModel):
    journal: str = Field(default="", description="Optional journal name to count entries for")

class CreateEntryWithAttachmentsArgs(BaseModel):
    content: str = Field(description="The text content of the journal entry")
    attachments: list[str] = Field(description="List of file paths to attach (max 10)")
    tags: list[str] = Field(default=[], description="Optional list of tags for the entry")
    journal: str = Field(default="", description="Optional journal name")
    starred: bool = Field(default=False, description="Mark entry as starred/important")

class CreateLocationEntryArgs(BaseModel):
    content: str = Field(description="The text content of the journal entry")
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")
    tags: list[str] = Field(default=[], description="Optional list of tags for the entry")
    journal: str = Field(default="", description="Optional journal name")
    starred: bool = Field(default=False, description="Mark entry as starred/important")

class ReadRecentEntriesArgs(BaseModel):
    limit: int = Field(default=10, description="Maximum number of entries to return (1-50)")
    journal: str = Field(default="", description="Optional journal name to filter by")

class SearchEntriesArgs(BaseModel):
    search_text: str = Field(description="Text to search for in entry content")
    limit: int = Field(default=20, description="Maximum number of entries to return (1-50)")
    journal: str = Field(default="", description="Optional journal name to filter by")

class ListJournalsFromDbArgs(BaseModel):
    pass

class GetEntryCountFromDbArgs(BaseModel):
    journal: str = Field(default="", description="Optional journal name to count entries for")

class GetEntriesByDateArgs(BaseModel):
    target_date: str = Field(description="Target date in MM-DD or YYYY-MM-DD format (e.g., '06-14' for June 14th)")
    years_back: int = Field(default=5, description="How many years back to search (default 5)")

class ReadFullEntryArgs(BaseModel):
    entry_uuid: str = Field(description="UUID of the entry to read in full")
    include_metadata: bool = Field(default=True, description="Include full metadata (tags, location, etc.)")

class UpdateEntryArgs(BaseModel):
    entry_uuid: str = Field(description="UUID of the entry to update")
    content: str = Field(description="New content to replace existing content")
    preserve_metadata: bool = Field(default=True, description="Whether to preserve existing metadata")

class AppendToEntryArgs(BaseModel):
    entry_uuid: str = Field(description="UUID of the entry to append to")
    content: str = Field(description="Content to append to existing entry")
    separator: str = Field(default="\n\n", description="Separator between existing and new content")

# Global Day One tools instance
dayone_tools: DayOneTools = None

def get_available_tools() -> list[Tool]:
    """Get list of available MCP tools."""
    return [
        Tool(
            name="create_journal_entry",
            description="Create a new entry in Day One journal with support for attachments, location, and metadata",
            inputSchema=CreateEntryArgs.model_json_schema(),
        ),
        Tool(
            name="list_journals",
            description="List all available Day One journals",
            inputSchema=ListJournalsArgs.model_json_schema(),
        ),
        Tool(
            name="get_entry_count",
            description="Get the total number of entries in a journal",
            inputSchema=GetEntryCountArgs.model_json_schema(),
        ),
        Tool(
            name="create_entry_with_attachments",
            description="Create a journal entry with file attachments (photos, videos, audio, PDFs)",
            inputSchema=CreateEntryWithAttachmentsArgs.model_json_schema(),
        ),
        Tool(
            name="create_location_entry",
            description="Create a journal entry with location coordinates",
            inputSchema=CreateLocationEntryArgs.model_json_schema(),
        ),
        Tool(
            name="read_recent_entries",
            description="Read recent journal entries from Day One database",
            inputSchema=ReadRecentEntriesArgs.model_json_schema(),
        ),
        Tool(
            name="search_entries",
            description="Search journal entries by text content",
            inputSchema=SearchEntriesArgs.model_json_schema(),
        ),
        Tool(
            name="list_journals_from_db",
            description="List all journals from database with entry counts",
            inputSchema=ListJournalsFromDbArgs.model_json_schema(),
        ),
        Tool(
            name="get_entry_count_from_db",
            description="Get actual entry count from Day One database",
            inputSchema=GetEntryCountFromDbArgs.model_json_schema(),
        ),
        Tool(
            name="get_entries_by_date",
            description="Get journal entries for a specific date across multiple years ('On This Day' feature)",
            inputSchema=GetEntriesByDateArgs.model_json_schema(),
        ),
        Tool(
            name="read_full_entry",
            description="Read a complete journal entry by UUID with full text content and metadata",
            inputSchema=ReadFullEntryArgs.model_json_schema(),
        ),
        Tool(
            name="update_entry",
            description="Update an existing journal entry by replacing its content completely",
            inputSchema=UpdateEntryArgs.model_json_schema(),
        ),
        Tool(
            name="append_to_entry", 
            description="Append content to an existing journal entry (more efficient than full update)",
            inputSchema=AppendToEntryArgs.model_json_schema(),
        ),
    ]

async def handle_create_journal_entry(args: CreateEntryArgs) -> list[TextContent]:
    """Handle creating a new journal entry."""
    try:
        uuid = dayone_tools.create_entry(
            content=args.content,
            tags=args.tags if args.tags else None,
            date=args.date if args.date else None,
            journal=args.journal if args.journal else None,
            attachments=args.attachments if args.attachments else None,
            starred=args.starred if args.starred else None,
            coordinates=args.coordinates if args.coordinates else None,
            timezone=args.timezone if args.timezone else None,
            all_day=args.all_day if args.all_day else None,
        )
        return [TextContent(
            type="text",
            text=f"Successfully created journal entry with UUID: {uuid}"
        )]
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error creating journal entry: {str(e)}"
        )]

async def handle_list_journals(args: ListJournalsArgs) -> list[TextContent]:
    """Handle listing available journals."""
    try:
        messages = dayone_tools.list_journals()
        journal_info = "\n".join(f"• {message}" for message in messages)
        return [TextContent(
            type="text",
            text=f"Journal Information:\n{journal_info}"
        )]
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error getting journal information: {str(e)}"
        )]

async def handle_get_entry_count(args: GetEntryCountArgs) -> list[TextContent]:
    """Handle getting entry count."""
    try:
        count = dayone_tools.get_entry_count(
            journal=args.journal if args.journal else None
        )
        journal_text = f" in journal '{args.journal}'" if args.journal else ""
        return [TextContent(
            type="text",
            text=f"Total entries{journal_text}: {count}"
        )]
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Entry count limitation: {str(e)}"
        )]

async def handle_create_entry_with_attachments(args: CreateEntryWithAttachmentsArgs) -> list[TextContent]:
    """Handle creating a journal entry with attachments."""
    try:
        uuid = dayone_tools.create_entry(
            content=args.content,
            attachments=args.attachments,
            tags=args.tags if args.tags else None,
            journal=args.journal if args.journal else None,
            starred=args.starred if args.starred else None,
        )
        attachment_count = len(args.attachments)
        return [TextContent(
            type="text",
            text=f"Successfully created journal entry with {attachment_count} attachment(s). UUID: {uuid}"
        )]
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error creating entry with attachments: {str(e)}"
        )]

async def handle_create_location_entry(args: CreateLocationEntryArgs) -> list[TextContent]:
    """Handle creating a journal entry with location."""
    try:
        coordinates = {
            "latitude": args.latitude,
            "longitude": args.longitude
        }
        uuid = dayone_tools.create_entry(
            content=args.content,
            coordinates=coordinates,
            tags=args.tags if args.tags else None,
            journal=args.journal if args.journal else None,
            starred=args.starred if args.starred else None,
        )
        return [TextContent(
            type="text",
            text=f"Successfully created location entry at {args.latitude}, {args.longitude}. UUID: {uuid}"
        )]
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error creating location entry: {str(e)}"
        )]

async def handle_read_recent_entries(args: ReadRecentEntriesArgs) -> list[TextContent]:
    """Handle reading recent journal entries."""
    try:
        # Validate limit
        limit = max(1, min(50, args.limit))
        
        entries = dayone_tools.read_recent_entries(
            limit=limit,
            journal=args.journal if args.journal else None
        )
        
        if not entries:
            return [TextContent(
                type="text",
                text="No entries found."
            )]
        
        # Format entries for display
        result_lines = [f"Found {len(entries)} recent entries:\n"]
        
        for i, entry in enumerate(entries, 1):
            date_str = entry['creation_date'].strftime("%Y-%m-%d %H:%M") if entry['creation_date'] else "Unknown date"
            starred_str = " ⭐" if entry['starred'] else ""
            tags_str = f" #{' #'.join(entry['tags'])}" if entry['tags'] else ""
            
            # Truncate text for preview - increased from 100 to 300 chars
            text_preview = entry['text'][:300] + "..." if len(entry['text']) > 300 else entry['text']
            
            result_lines.append(
                f"{i}. {date_str}{starred_str} [{entry['journal_name']}] (UUID: {entry['uuid']})\n"
                f"   {text_preview}{tags_str}\n"
            )
        
        return [TextContent(
            type="text",
            text="\n".join(result_lines)
        )]
        
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error reading entries: {str(e)}"
        )]

async def handle_search_entries(args: SearchEntriesArgs) -> list[TextContent]:
    """Handle searching journal entries."""
    try:
        # Validate limit
        limit = max(1, min(50, args.limit))
        
        entries = dayone_tools.search_entries(
            search_text=args.search_text,
            limit=limit,
            journal=args.journal if args.journal else None
        )
        
        if not entries:
            return [TextContent(
                type="text",
                text=f"No entries found matching '{args.search_text}'."
            )]
        
        # Format search results
        result_lines = [f"Found {len(entries)} entries matching '{args.search_text}':\n"]
        
        for i, entry in enumerate(entries, 1):
            date_str = entry['creation_date'].strftime("%Y-%m-%d %H:%M") if entry['creation_date'] else "Unknown date"
            starred_str = " ⭐" if entry['starred'] else ""
            tags_str = f" #{' #'.join(entry['tags'])}" if entry['tags'] else ""
            
            # Show more context for search results - increased from 200 to 400 chars
            text_preview = entry['text'][:400] + "..." if len(entry['text']) > 400 else entry['text']
            
            result_lines.append(
                f"{i}. {date_str}{starred_str} [{entry['journal_name']}] (UUID: {entry['uuid']})\n"
                f"   {text_preview}{tags_str}\n"
            )
        
        return [TextContent(
            type="text",
            text="\n".join(result_lines)
        )]
        
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error searching entries: {str(e)}"
        )]

async def handle_list_journals_from_db(args: ListJournalsFromDbArgs) -> list[TextContent]:
    """Handle listing journals from database."""
    try:
        journals = dayone_tools.list_journals_from_db()
        
        if not journals:
            return [TextContent(
                type="text",
                text="No journals found in database."
            )]
        
        # Format journal list
        result_lines = ["Your Day One Journals:\n"]
        
        for journal in journals:
            last_entry_str = ""
            if journal['last_entry_date']:
                last_entry_str = f" (last entry: {journal['last_entry_date'].strftime('%Y-%m-%d')})"
            
            result_lines.append(
                f"• {journal['name']}: {journal['entry_count']} entries{last_entry_str}"
            )
        
        total_entries = sum(j['entry_count'] for j in journals)
        result_lines.append(f"\nTotal: {len(journals)} journals, {total_entries} entries")
        
        return [TextContent(
            type="text",
            text="\n".join(result_lines)
        )]
        
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error listing journals: {str(e)}"
        )]

async def handle_get_entry_count_from_db(args: GetEntryCountFromDbArgs) -> list[TextContent]:
    """Handle getting entry count from database."""
    try:
        count = dayone_tools.get_entry_count_from_db(
            journal=args.journal if args.journal else None
        )
        
        journal_text = f" in journal '{args.journal}'" if args.journal else ""
        return [TextContent(
            type="text",
            text=f"Total entries{journal_text}: {count}"
        )]
        
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error getting entry count: {str(e)}"
        )]

async def handle_get_entries_by_date(args: GetEntriesByDateArgs) -> list[TextContent]:
    """Handle getting entries by date ('On This Day')."""
    try:
        entries = dayone_tools.get_entries_by_date(
            target_date=args.target_date,
            years_back=args.years_back
        )
        
        if not entries:
            return [TextContent(
                type="text",
                text=f"No entries found for {args.target_date} in the past {args.years_back} years."
            )]
        
        # Group entries by year for better display
        from collections import defaultdict
        entries_by_year = defaultdict(list)
        for entry in entries:
            entries_by_year[entry['year']].extend([entry])
        
        # Format results
        result_lines = [f"📅 On This Day ({args.target_date}) - Found {len(entries)} entries:\n"]
        
        # Sort years in descending order (most recent first)
        for year in sorted(entries_by_year.keys(), reverse=True):
            year_entries = entries_by_year[year]
            years_ago = year_entries[0]['years_ago']
            
            if years_ago == 0:
                year_header = f"🗓️ {year} (This year):"
            elif years_ago == 1:
                year_header = f"🗓️ {year} (1 year ago):"
            else:
                year_header = f"🗓️ {year} ({years_ago} years ago):"
            
            result_lines.append(year_header)
            
            for entry in year_entries:
                date_str = entry['creation_date'].strftime("%B %d, %Y at %H:%M") if entry['creation_date'] else "Unknown date"
                starred_str = " ⭐" if entry['starred'] else ""
                tags_str = f" #{' #'.join(entry['tags'])}" if entry['tags'] else ""
                
                # Show more content for "On This Day" memories - increased from 300 to 500
                text_preview = entry['text'][:500] + "..." if len(entry['text']) > 500 else entry['text']
                
                result_lines.append(
                    f"   • {date_str}{starred_str} [{entry['journal_name']}] (UUID: {entry['uuid']})\n"
                    f"     {text_preview}{tags_str}\n"
                )
        
        return [TextContent(
            type="text",
            text="\n".join(result_lines)
        )]
        
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error getting entries by date: {str(e)}"
        )]

async def handle_read_full_entry(args: ReadFullEntryArgs) -> list[TextContent]:
    """Handle reading a complete journal entry by UUID."""
    try:
        entry = dayone_tools.read_full_entry_by_uuid(
            entry_uuid=args.entry_uuid,
            include_metadata=args.include_metadata
        )
        
        if not entry:
            return [TextContent(
                type="text",
                text=f"No entry found with UUID: {args.entry_uuid}"
            )]
        
        # Format the complete entry
        result_lines = []
        
        # Header with metadata
        date_str = entry['creation_date'].strftime("%A, %B %d, %Y at %H:%M") if entry['creation_date'] else "Unknown date"
        starred_str = " ⭐" if entry['starred'] else ""
        
        result_lines.append(f"📖 Journal Entry{starred_str}")
        result_lines.append(f"📅 {date_str}")
        result_lines.append(f"📚 Journal: {entry['journal_name']}")
        
        if args.include_metadata:
            if entry['tags']:
                result_lines.append(f"🏷️ Tags: #{' #'.join(entry['tags'])}")
            
            if entry['timezone']:
                result_lines.append(f"🌍 Timezone: {entry['timezone']}")
            
            if entry['has_location']:
                result_lines.append(f"📍 Has location data")
            
            if entry['has_weather']:
                result_lines.append(f"☀️ Has weather data")
            
            if entry['modified_date'] and entry['modified_date'] != entry['creation_date']:
                mod_date_str = entry['modified_date'].strftime("%Y-%m-%d %H:%M")
                result_lines.append(f"✏️ Last modified: {mod_date_str}")
        
        result_lines.append(f"🆔 UUID: {entry['uuid']}")
        result_lines.append("")  # Empty line before content
        result_lines.append("📝 Content:")
        result_lines.append("-" * 40)
        result_lines.append(entry['text'])
        result_lines.append("-" * 40)
        
        return [TextContent(
            type="text",
            text="\n".join(result_lines)
        )]
        
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error reading full entry: {str(e)}"
        )]

async def handle_update_entry(args: UpdateEntryArgs) -> list[TextContent]:
    """Handle updating an existing journal entry."""
    try:
        updated_entry = dayone_tools.update_entry(
            entry_uuid=args.entry_uuid,
            content=args.content,
            preserve_metadata=args.preserve_metadata
        )
        
        if not updated_entry:
            return [TextContent(
                type="text",
                text=f"Failed to update entry with UUID: {args.entry_uuid}"
            )]
        
        # Format response with updated entry info
        date_str = updated_entry['creation_date'].strftime("%A, %B %d, %Y at %H:%M") if updated_entry['creation_date'] else "Unknown date"
        modified_str = updated_entry['modified_date'].strftime("%Y-%m-%d %H:%M:%S") if updated_entry['modified_date'] else "Unknown"
        
        return [TextContent(
            type="text",
            text=f"✅ Successfully updated journal entry!\n\n"
                 f"📖 Entry: {date_str}\n"
                 f"🔄 Last Modified: {modified_str}\n"
                 f"📚 Journal: {updated_entry['journal_name']}\n"
                 f"🆔 UUID: {args.entry_uuid}\n\n"
                 f"Content preview: {updated_entry['text'][:200]}{'...' if len(updated_entry['text']) > 200 else ''}"
        )]
        
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"❌ Error updating entry: {str(e)}"
        )]

async def handle_append_to_entry(args: AppendToEntryArgs) -> list[TextContent]:
    """Handle appending content to an existing journal entry."""
    try:
        updated_entry = dayone_tools.append_to_entry(
            entry_uuid=args.entry_uuid,
            content=args.content,
            separator=args.separator
        )
        
        if not updated_entry:
            return [TextContent(
                type="text",
                text=f"Failed to append to entry with UUID: {args.entry_uuid}"
            )]
        
        # Format response with updated entry info
        date_str = updated_entry['creation_date'].strftime("%A, %B %d, %Y at %H:%M") if updated_entry['creation_date'] else "Unknown date"
        modified_str = updated_entry['modified_date'].strftime("%Y-%m-%d %H:%M:%S") if updated_entry['modified_date'] else "Unknown"
        
        return [TextContent(
            type="text",
            text=f"✅ Successfully appended to journal entry!\n\n"
                 f"📖 Entry: {date_str}\n"
                 f"🔄 Last Modified: {modified_str}\n"
                 f"📚 Journal: {updated_entry['journal_name']}\n"
                 f"🆔 UUID: {args.entry_uuid}\n\n"
                 f"📎 Appended content: {args.content[:100]}{'...' if len(args.content) > 100 else ''}\n"
                 f"📄 Total length: {len(updated_entry['text'])} characters"
        )]
        
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"❌ Error appending to entry: {str(e)}"
        )]


async def main():
    """Main server entry point."""
    global dayone_tools
    
    # Initialize Day One tools with enhanced logging
    try:
        logger.info("🔄 Initializing Day One tools...")
        dayone_tools = DayOneTools()
        logger.info("✅ Day One CLI verified successfully")
        
        # Test basic functionality to ensure everything is ready
        logger.info("🧪 Testing Day One functionality...")
        try:
            db_conn = dayone_tools._get_db_connection()
            db_conn.close()
            logger.info("✅ Database connection test successful")
        except Exception as e:
            logger.warning(f"⚠️ Database test failed (but continuing): {e}")
        
        logger.info("🚀 Day One tools fully initialized and ready")
        
    except DayOneError as e:
        logger.error(f"❌ Failed to initialize Day One tools: {e}")
        return 1

    # Create and run server
    async with stdio_server() as (read_stream, write_stream):
        server = Server("mcp-dayone")
        
        # Register handlers with request logging
        @server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            log_mcp_request({"method": "tools/list", "timestamp": datetime.datetime.now().isoformat()}, "tools_list_request")
            return get_available_tools()
        
        @server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            try:
                # 🔍 Log the tool call request
                request_data = {
                    "method": "tools/call",
                    "tool_name": name,
                    "arguments": arguments,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                log_mcp_request(request_data, "tool_call_request")
                
                # 🐛 DEBUG: Log what we actually receive (keep existing debug)
                logger.info(f"🔧 Tool called: {name}")
                logger.info(f"📥 Arguments received: {arguments}")
                logger.info(f"📝 Arguments type: {type(arguments)}")
                
                if name == "create_journal_entry":
                    args = CreateEntryArgs(**arguments)
                    return await handle_create_journal_entry(args)
                elif name == "list_journals":
                    args = ListJournalsArgs(**arguments)
                    return await handle_list_journals(args)
                elif name == "get_entry_count":
                    args = GetEntryCountArgs(**arguments)
                    return await handle_get_entry_count(args)
                elif name == "create_entry_with_attachments":
                    args = CreateEntryWithAttachmentsArgs(**arguments)
                    return await handle_create_entry_with_attachments(args)
                elif name == "create_location_entry":
                    args = CreateLocationEntryArgs(**arguments)
                    return await handle_create_location_entry(args)
                elif name == "read_recent_entries":
                    args = ReadRecentEntriesArgs(**arguments)
                    return await handle_read_recent_entries(args)
                elif name == "search_entries":
                    args = SearchEntriesArgs(**arguments)
                    return await handle_search_entries(args)
                elif name == "list_journals_from_db":
                    args = ListJournalsFromDbArgs(**arguments)
                    return await handle_list_journals_from_db(args)
                elif name == "get_entry_count_from_db":
                    args = GetEntryCountFromDbArgs(**arguments)
                    return await handle_get_entry_count_from_db(args)
                elif name == "get_entries_by_date":
                    args = GetEntriesByDateArgs(**arguments)
                    return await handle_get_entries_by_date(args)
                elif name == "read_full_entry":
                    args = ReadFullEntryArgs(**arguments)
                    return await handle_read_full_entry(args)
                elif name == "update_entry":
                    args = UpdateEntryArgs(**arguments)
                    return await handle_update_entry(args)
                elif name == "append_to_entry":
                    args = AppendToEntryArgs(**arguments)
                    return await handle_append_to_entry(args)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            
            except Exception as e:
                logger.error(f"Error in call_tool: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        # Run the server  
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-dayone",
                server_version="2.0.0",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(listChanged=False)
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())