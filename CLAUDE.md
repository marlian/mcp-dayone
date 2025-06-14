# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an MCP (Message Control Protocol) server that provides integration between Claude Desktop and Day One Journal. The server implements the MCP protocol to enable Claude to create journal entries, list journals, and manage Day One data through proper tool calls.

## Project Status - Migration to Python MCP

**Current Phase**: Migrating from Node.js REST API to Python MCP server
**Progress**: Core MCP implementation completed

### Migration Progress:
- ✅ Created Python project structure with uv/pyproject.toml
- ✅ Implemented proper MCP protocol server 
- ✅ Created Day One CLI wrapper tools
- ✅ Defined MCP tool schemas and handlers
- 🔄 Updating documentation and installation instructions

## Architecture

### New Python MCP Structure:
- **src/mcp_dayone/server.py**: Main MCP server with tool handlers
- **src/mcp_dayone/tools.py**: Day One CLI wrapper and operations
- **pyproject.toml**: Python project dependencies and configuration
- **.python-version**: Python version specification (3.11)

### Legacy Node.js Files (to be removed):
- **server.js**: Old Express.js REST API server
- **claude-desktop.js**: Old client-side integration script
- **test.js**: Old HTTP test client

## Common Commands

### Development (New Python MCP)
- `uv sync` - Install dependencies and create virtual environment
- `uv run python -m mcp_dayone.server` - Run MCP server
- `uv run pytest` - Run tests (when implemented)

### Legacy Commands (Node.js - deprecated)
- `npm start` - Start old REST server
- `npm run dev` - Start with nodemon

## Dependencies

### Required System Dependencies
- Day One CLI (`dayone2`) - Must be installed and accessible in PATH
- Python 3.11+
- uv package manager

### Python Dependencies
- mcp>=1.0.0 - MCP protocol implementation
- click>=8.0.0 - CLI utilities
- pydantic>=2.0.0 - Data validation

## MCP Tools Available

1. **create_journal_entry** - Create new Day One entries
2. **list_journals** - List available journals
3. **get_entry_count** - Get entry count for journals

## Claude Desktop Integration

The server uses MCP protocol over stdio. Configuration will be added to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dayone": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-dayone", "run", "python", "-m", "mcp_dayone.server"]
    }
  }
}
```