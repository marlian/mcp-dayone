# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an MCP (Message Control Protocol) server that provides integration between Claude Desktop and Day One Journal. The server implements the MCP protocol to enable Claude to create journal entries, list journals, and manage Day One data through proper tool calls.

## Project Status - Migration to Python MCP

**Current Phase**: Migration to Python MCP completed ✅
**Progress**: Ready for production use

### Migration Progress:
- ✅ Created Python project structure with uv/pyproject.toml
- ✅ Implemented proper MCP protocol server 
- ✅ Created Day One CLI wrapper tools
- ✅ Defined MCP tool schemas and handlers
- ✅ Updated documentation and installation instructions
- ✅ Created comprehensive README with setup guide
- ✅ Added setup test script for validation
- ✅ Tested uv sync installation process

## Architecture

### New Python MCP Structure:
- **src/mcp_dayone/server.py**: Main MCP server with tool handlers
- **src/mcp_dayone/tools.py**: Day One CLI wrapper and operations
- **pyproject.toml**: Python project dependencies and configuration
- **.python-version**: Python version specification (3.11)

### Removed Legacy Files:
- ~~**server.js**: Old Express.js REST API server~~ (removed)
- ~~**claude-desktop.js**: Old client-side integration script~~ (removed)
- ~~**test.js**: Old HTTP test client~~ (removed)
- ~~**package.json, package-lock.json, node_modules/**: Node.js artifacts~~ (removed)

## Common Commands

### Development (New Python MCP)
- `uv sync` - Install dependencies and create virtual environment
- `uv run python -m mcp_dayone.server` - Run MCP server directly
- `uv run python test_setup.py` - Test installation and Day One CLI
- `uv run pytest` - Run tests (when implemented)

### Getting Started
1. Install Day One app and CLI from [Day One CLI Guide](https://dayoneapp.com/guides/tips-and-tutorials/command-line-interface-cli)
2. Verify CLI access: `dayone2 --version`
3. Install project: `uv sync`
4. Test setup: `uv run python test_setup.py`
5. Configure Claude Desktop with absolute path to this project

### Legacy Commands (Node.js - removed)
- ~~`npm start` - Start old REST server~~ (removed)
- ~~`npm run dev` - Start with nodemon~~ (removed)

## Dependencies

### Required System Dependencies
- **Day One CLI** (`dayone2`) - Install from [Day One CLI Guide](https://dayoneapp.com/guides/tips-and-tutorials/command-line-interface-cli). Must be accessible in PATH.
- **Python 3.11+** 
- **uv package manager** - Install from [astral.sh](https://astral.sh/uv/install.sh)

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