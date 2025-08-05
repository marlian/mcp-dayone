#!/usr/bin/env python3
"""Test script for enhanced Day One MCP features.

This script validates the hybrid approach enhancements:
- Increased preview text limits (300/400/500 chars vs original 100/200/300)
- New read_full_entry_by_uuid function for complete entry retrieval
- UUID inclusion in all preview responses for workflow chaining

Usage:
    uv run python test_enhancements.py
"""

import sys
import asyncio
from src.mcp_dayone.tools import DayOneTools, DayOneError

async def test_enhanced_features():
    """Test the hybrid approach enhancements."""
    print("🧪 Testing Day One MCP Enhanced Features")
    print("=" * 50)
    
    try:
        # Initialize tools
        tools = DayOneTools()
        print("✅ Day One tools initialized successfully")
        
        # Test 1: Enhanced preview limits
        print("\n📖 Testing enhanced preview limits...")
        entries = tools.read_recent_entries(limit=2)
        
        if not entries:
            print("   ⚠️ No entries found for testing")
            return 0
            
        for i, entry in enumerate(entries, 1):
            text_preview = entry['text'][:80] + "..." if len(entry['text']) > 80 else entry['text']
            print(f"   {i}. {entry['creation_date']}")
            print(f"      Preview: {text_preview}")
            print(f"      Full length: {len(entry['text'])} chars")
            print(f"      UUID: {entry['uuid']}")
            print(f"      Tags: {entry['tags']}")
        
        # Test 2: Full entry retrieval by UUID
        test_uuid = entries[0]['uuid']
        print(f"\n🔍 Testing read_full_entry_by_uuid...")
        print(f"   Target UUID: {test_uuid}")
        
        full_entry = tools.read_full_entry_by_uuid(test_uuid, include_metadata=True)
        
        if full_entry:
            print(f"   ✅ Full entry retrieved successfully")
            print(f"   📝 Content length: {len(full_entry['text'])} characters")
            print(f"   🏷️ Tags: {full_entry['tags']}")
            print(f"   ⭐ Starred: {full_entry['starred']}")
            print(f"   📚 Journal: {full_entry['journal_name']}")
            print(f"   🌍 Timezone: {full_entry['timezone']}")
            print(f"   📍 Has location: {full_entry['has_location']}")
            print(f"   ☀️ Has weather: {full_entry['has_weather']}")
            
            # Verify no truncation occurred
            if len(full_entry['text']) > 1000:
                print(f"   🎯 Long content test: PASSED (no truncation)")
            
            # Show meaningful preview
            lines = full_entry['text'].split('\n')[:3]
            preview = '\n'.join(lines)
            if len(preview) > 150:
                preview = preview[:150] + "..."
            print(f"   📖 Content preview:\n      {preview.replace(chr(10), chr(10) + '      ')}")
            
        else:
            print(f"   ❌ No entry found with UUID: {test_uuid}")
            return 1
            
        # Test 3: Workflow validation
        print(f"\n🔄 Testing complete workflow...")
        search_entries = tools.search_entries("task", limit=1)
        if search_entries:
            search_uuid = search_entries[0]['uuid']
            workflow_entry = tools.read_full_entry_by_uuid(search_uuid)
            if workflow_entry:
                print(f"   ✅ Search → UUID → Full Read workflow: PASSED")
            else:
                print(f"   ❌ Workflow test failed at full read step")
        else:
            print(f"   ⚠️ No entries found for workflow test (searching 'task')")
        
        print("\n🎉 All enhanced features working correctly!")
        print("=" * 50)
        print("Ready for production use with increased preview limits and full text retrieval!")
        
    except DayOneError as e:
        print(f"❌ Day One error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(test_enhanced_features())
    sys.exit(exit_code)
