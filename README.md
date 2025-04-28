# MCP-DayOne

A Message Control Protocol (MCP) server for Day One Journal integration with Claude Desktop and Smithery.

## Overview

This server provides an API interface to the Day One CLI (`dayone2`), allowing Claude Desktop and other applications to interact with your Day One journal.

## Prerequisites

- Day One CLI (`dayone2`) installed on your system
- Node.js and npm

## Installation

1. Clone this repository
2. Run `npm install` to install dependencies
3. Create a `.env` file (see `.env.example`)
4. Run `npm start` to start the server

## API Endpoints

### POST /api/entry

Creates a new entry in your Day One journal.

**Request Body:**

```json
{
  "content": "Your journal entry text",
  "tags": ["optional", "tags"],
  "date": "YYYY-MM-DD HH:MM:SS", // Optional
  "journal": "Journal Name" // Optional
}
```

**Response:**

```json
{
  "success": true,
  "result": "Created new entry with uuid: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
```

### GET /health

Check if the server is running.

**Response:**

```json
{
  "status": "ok"
}
```

## Integration with Claude Desktop

This MCP server can be used with Claude Desktop to create journal entries automatically.

## Integration with Smithery

This project can be shared on [Smithery](https://smithery.ai/) to allow others to use and contribute to it.

