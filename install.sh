#!/bin/bash

echo "Installing MCP-DayOne..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Day One CLI is installed
if ! command -v dayone2 &> /dev/null; then
    echo "Day One CLI (dayone2) is not installed. Please install it first."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Create .env file if it doesn"t exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo "MCP-DayOne installed successfully!"
