"""MCP server for Day One Journal integration."""

import asyncio
import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
)
from pydantic import BaseModel, Field

from .tools import DayOneTools, DayOneError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        journals = dayone_tools.list_journals()
        if journals:
            journal_list = "\n".join(f"• {journal}" for journal in journals)
            return [TextContent(
                type="text",
                text=f"Available journals:\n{journal_list}"
            )]
        else:
            return [TextContent(
                type="text",
                text="No journals found."
            )]
    except DayOneError as e:
        return [TextContent(
            type="text",
            text=f"Error listing journals: {str(e)}"
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
            text=f"Error getting entry count: {str(e)}"
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

async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls from Claude."""
    try:
        if request.name == "create_journal_entry":
            args = CreateEntryArgs(**request.arguments)
            content = await handle_create_journal_entry(args)
        elif request.name == "list_journals":
            args = ListJournalsArgs(**request.arguments)
            content = await handle_list_journals(args)
        elif request.name == "get_entry_count":
            args = GetEntryCountArgs(**request.arguments)
            content = await handle_get_entry_count(args)
        elif request.name == "create_entry_with_attachments":
            args = CreateEntryWithAttachmentsArgs(**request.arguments)
            content = await handle_create_entry_with_attachments(args)
        elif request.name == "create_location_entry":
            args = CreateLocationEntryArgs(**request.arguments)
            content = await handle_create_location_entry(args)
        else:
            raise ValueError(f"Unknown tool: {request.name}")
        
        return CallToolResult(content=content)
    
    except Exception as e:
        logger.error(f"Error in call_tool: {e}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )],
            isError=True,
        )

async def list_tools(request: ListToolsRequest) -> list[Tool]:
    """List available tools."""
    return get_available_tools()

async def main():
    """Main server entry point."""
    global dayone_tools
    
    # Initialize Day One tools
    try:
        dayone_tools = DayOneTools()
        logger.info("Day One CLI verified successfully")
    except DayOneError as e:
        logger.error(f"Failed to initialize Day One tools: {e}")
        return 1
    
    # Create and run server
    async with stdio_server() as (read_stream, write_stream):
        server = Server("mcp-dayone")
        
        # Register handlers
        server.list_tools = list_tools
        server.call_tool = call_tool
        
        # Initialize options
        options = InitializationOptions(
            server_name="mcp-dayone",
            server_version="2.0.0",
            capabilities=server.get_capabilities(
                notification_options=None,
                experimental_capabilities=None,
            ),
        )
        
        await server.run(
            read_stream,
            write_stream,
            options,
        )

if __name__ == "__main__":
    asyncio.run(main())