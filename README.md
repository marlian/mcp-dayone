# MCP-DayOne

A Message Control Protocol (MCP) server for Day One Journal integration with Claude Desktop.

## Overview

This MCP server enables Claude Desktop to interact with your Day One journal through the Model Context Protocol. Claude can create journal entries, list available journals, and get entry counts directly through natural conversation.

## Features

- 📝 Create journal entries with content, tags, dates, and journal selection
- 📚 List all available Day One journals
- 📊 Get entry counts for journals
- 🔧 Proper error handling and validation
- 🚀 Easy installation with `uv`

## Prerequisites

- **Day One CLI** (`dayone2`) - [Install from Day One website](https://dayoneapp.com/guides/command-line-interface/)
- **Python 3.11+** 
- **uv** - [Install from astral.sh](https://astral.sh/uv/install.sh)

## Installation

### 1. Install Prerequisites

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify Day One CLI is installed
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

### 4. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP server.

## Usage

Once configured, you can interact with Day One through Claude Desktop:

- **"Create a journal entry about my day"** - Claude will create an entry with your content
- **"List my Day One journals"** - Shows all available journals
- **"How many entries do I have?"** - Shows total entry count
- **"Add tags #work #meeting to an entry about the team standup"** - Creates tagged entries

## Available MCP Tools

1. **create_journal_entry**
   - Create new Day One entries
   - Parameters: content, tags, date, journal
   
2. **list_journals**
   - List all available journals
   
3. **get_entry_count**
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
- Install from: https://dayoneapp.com/guides/command-line-interface/

### Claude Desktop Connection Issues
- Verify the absolute path in `claude_desktop_config.json`
- Check Claude Desktop logs for MCP server errors
- Restart Claude Desktop after configuration changes

### Permission Issues
- Ensure Day One CLI has proper permissions to access your journals
- Run Day One app once to initialize if needed

## License

MIT

