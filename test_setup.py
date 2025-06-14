#!/usr/bin/env python3
"""Test script to verify MCP-DayOne setup."""

import sys
from mcp_dayone.tools import DayOneTools, DayOneError

def test_dayone_cli():
    """Test Day One CLI availability."""
    print("🔍 Testing Day One CLI availability...")
    
    try:
        tools = DayOneTools()
        print("✅ Day One CLI found and working")
        
        # Test listing journals
        try:
            journals = tools.list_journals()
            print(f"✅ Found {len(journals)} journals: {', '.join(journals) if journals else 'None'}")
        except DayOneError as e:
            print(f"⚠️  Could not list journals: {e}")
            
    except DayOneError as e:
        print(f"❌ Day One CLI not available: {e}")
        print("   Install Day One CLI from: https://dayoneapp.com/guides/command-line-interface/")
        return False
    
    return True

def test_mcp_server():
    """Test MCP server can be imported."""
    print("\n🔍 Testing MCP server import...")
    
    try:
        from mcp_dayone.server import main, get_available_tools
        tools = get_available_tools()
        print(f"✅ MCP server imported successfully")
        print(f"✅ Available tools: {[tool.name for tool in tools]}")
        return True
    except Exception as e:
        print(f"❌ MCP server import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 MCP-DayOne Setup Test\n")
    
    tests_passed = 0
    total_tests = 2
    
    if test_mcp_server():
        tests_passed += 1
    
    if test_dayone_cli():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! MCP-DayOne is ready to use.")
        print("\n📋 Next steps:")
        print("1. Add MCP server configuration to Claude Desktop")
        print("2. Restart Claude Desktop")
        print("3. Test with Claude: 'List my Day One journals'")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()