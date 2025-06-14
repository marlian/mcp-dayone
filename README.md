# MCP-DayOne

A Message Control Protocol (MCP) server for Day One Journal integration with Claude Desktop.

## Overview

This MCP server enables Claude Desktop to interact with your Day One journal through the Model Context Protocol. Claude can create journal entries, list available journals, and get entry counts directly through natural conversation.

## Features

### ✍️ **Write Operations (Day One CLI)**
- 📝 Create journal entries with rich content and metadata
- 📎 Add attachments (photos, videos, audio, PDFs) to entries
- ⭐ Mark entries as starred/important
- 📍 Add location coordinates to entries
- 🕐 Enhanced date/time handling with timezone support

### 📖 **Read Operations (Direct Database Access)**
- 📖 **NEW**: Read recent journal entries with full metadata
- 🔍 **NEW**: Search entries by text content
- 📚 **NEW**: List actual journals with entry counts and statistics
- 📊 **NEW**: Get real entry counts from database
- 🏷️ **NEW**: View entry tags, dates, and metadata

### 🔧 **Technical**
- Proper error handling and validation
- Direct SQLite database integration for read operations
- Hybrid approach: CLI for writing, database for reading
- 🚀 Easy installation with `uv`

## Prerequisites

- **Day One CLI** (`dayone2`) - [Install from Day One website](https://dayoneapp.com/guides/tips-and-tutorials/command-line-interface-cli)
- **Python 3.11+** 
- **uv** - [Install from astral.sh](https://astral.sh/uv/install.sh)

## Installation

### 1. Install Prerequisites

**Day One CLI Installation:**
1. Download and install Day One from the Mac App Store or Day One website
2. Install the Day One CLI following the [official CLI guide](https://dayoneapp.com/guides/tips-and-tutorials/command-line-interface-cli)
3. The CLI is included with Day One and accessible via the `dayone2` command

**Python and uv:**
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify Day One CLI is installed and accessible
dayone2 --version
```

### 2. Clone and Setup

```bash
git clone <repository-url>
cd mcp-dayone
uv sync
```

### 3. Configure Claude Desktop

Add the following to your Claude Desktop configuration file:

**Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "dayone": {
      "command": "uv",
      "args": [
        "--directory",
        "/FULL/PATH/TO/mcp-dayone",
        "run",
        "python",
        "-m",
        "mcp_dayone.server"
      ]
    }
  }
}
```

**Important:** Replace `/FULL/PATH/TO/mcp-dayone` with the absolute path to your cloned repository.

### 4. Test Installation (Optional)

Verify everything is working:
```bash
# Test Day One CLI access
dayone2 --version

# Test MCP server setup
uv run python test_setup.py
```

### 5. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP server.

## Usage

Once configured, you can interact with Day One through Claude Desktop:

### ✍️ **Creating Entries**
- **"Create a journal entry about my day"** - Creates entry with your content
- **"Create a starred entry about my vacation with photos from /path/to/photo.jpg"** - Creates entries with attachments and metadata
- **"Add a journal entry with location coordinates for my current trip"** - Creates location-aware entries
- **"Add tags #work #meeting to an entry about the team standup"** - Creates tagged entries

### 📖 **Reading & Searching**
- **"Show me my recent journal entries"** - Displays recent entries with dates, tags, and previews
- **"Search my journal for entries about work"** - Finds entries containing specific text
- **"What were my journal entries on this day?"** - **NEW**: Shows "On This Day" entries from previous years
- **"Show me entries from June 14th in past years"** - **NEW**: Date-specific historical entries
- **"List my Day One journals with entry counts"** - Shows actual journals and statistics
- **"How many entries do I have?"** - Gets real entry counts from database
- **"Find entries from last week"** - Search by date ranges

## Available MCP Tools

### ✍️ **Write Tools (CLI-based)**
1. **create_journal_entry** - Create entries with rich metadata (attachments, location, tags, etc.)
2. **create_entry_with_attachments** - Specialized for file attachments (photos, videos, audio, PDFs)
3. **create_location_entry** - Specialized for location-aware entries with coordinates

### 📖 **Read Tools (Database-based)**
4. **read_recent_entries** - **NEW**: Read recent journal entries with full metadata
   - Parameters: limit (1-50), journal (optional filter)
   - Returns: Formatted entries with dates, tags, previews, starred status

5. **search_entries** - **NEW**: Search entries by text content
   - Parameters: search_text, limit (1-50), journal (optional filter)
   - Returns: Matching entries with context and metadata

6. **list_journals_from_db** - **NEW**: List actual journals with statistics
   - Returns: Journal names, entry counts, last entry dates

7. **get_entry_count_from_db** - **NEW**: Get real entry counts
   - Parameters: journal (optional filter)
   - Returns: Actual entry count from database

8. **get_entries_by_date** - **NEW**: Get "On This Day" entries from previous years
   - Parameters: target_date (MM-DD or YYYY-MM-DD), years_back (default 5)
   - Returns: Entries from the same date across multiple years with full content

### 📋 **Legacy Tools (CLI limitations)**
9. **list_journals** - Provides guidance about CLI limitations
10. **get_entry_count** - Explains CLI counting limitations

## Development

```bash
# Install development dependencies
uv sync --dev

# Run the server directly (for testing)
uv run python -m mcp_dayone.server

# Run tests (when implemented)
uv run pytest
```

## Troubleshooting

### Day One CLI Not Found
- Verify Day One CLI is installed: `dayone2 --version`  
- Check that `dayone2` is in your PATH
- Install Day One app and CLI from: https://dayoneapp.com/guides/tips-and-tutorials/command-line-interface-cli

### Claude Desktop Connection Issues
- Verify the absolute path in `claude_desktop_config.json`
- Check Claude Desktop logs for MCP server errors
- Restart Claude Desktop after configuration changes

### Permission Issues
- Ensure Day One CLI has proper permissions to access your journals
- Run Day One app once to initialize if needed

### CLI Limitations
- Day One CLI only supports creating entries (`new` command)
- Listing journals and counting entries are not supported by the CLI
- Use the Day One app interface to view journals and entry counts
- All entry creation features (attachments, location, etc.) work fully

## License

MIT

