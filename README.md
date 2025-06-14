# MCP-DayOne

A Message Control Protocol (MCP) server for Day One Journal integration with Claude Desktop.

## Overview

This MCP server enables Claude Desktop to interact with your Day One journal through the Model Context Protocol. Claude can create journal entries, list available journals, and get entry counts directly through natural conversation.

## Features

- 📝 Create journal entries with rich content and metadata
- 📎 **NEW**: Add attachments (photos, videos, audio, PDFs) to entries
- ⭐ **NEW**: Mark entries as starred/important
- 📍 **NEW**: Add location coordinates to entries
- 🕐 **NEW**: Enhanced date/time handling with timezone support
- 📚 List all available Day One journals
- 📊 Get entry counts for journals
- 🔧 Proper error handling and validation
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

- **"Create a journal entry about my day"** - Claude will create an entry with your content
- **"Create a starred entry about my vacation with photos from /path/to/photo.jpg"** - Creates entries with attachments and metadata
- **"Add a journal entry with location coordinates for my current trip"** - Creates location-aware entries
- **"List my Day One journals"** - Shows all available journals
- **"How many entries do I have?"** - Shows total entry count
- **"Add tags #work #meeting to an entry about the team standup"** - Creates tagged entries

## Available MCP Tools

1. **create_journal_entry** (Enhanced)
   - Create new Day One entries with rich metadata
   - **Basic Parameters**: content, tags, date, journal
   - **Enhanced Features**: attachments, starred, coordinates, timezone, all_day
   
2. **create_entry_with_attachments** (NEW)
   - Specialized tool for creating entries with file attachments
   - Supports photos, videos, audio, PDFs (up to 10 files)
   - Parameters: content, attachments, tags, journal, starred
   
3. **create_location_entry** (NEW)
   - Specialized tool for creating location-aware entries
   - Add precise latitude/longitude coordinates
   - Parameters: content, latitude, longitude, tags, journal, starred
   
4. **list_journals**
   - List all available journals
   
5. **get_entry_count**
   - Get entry count for specific journal or all journals

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

## License

MIT

