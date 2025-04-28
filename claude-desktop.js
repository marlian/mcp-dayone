// Claude Desktop integration for Day One Journal

/**
 * This is a client-side script that integrates with the MCP-DayOne server
 * to create journal entries from Claude Desktop conversations.
 */

const MCP_SERVER_URL = http://localhost:3000;

/**
 * Create a new Day One journal entry from the current Claude Desktop conversation
 */
async function createJournalEntry() {
  // Get the conversation content
  const conversation = await window.claudeDesktop.getCurrentConversation();
  
  // Format the conversation content
  let content = `# Conversation with Claude - ${new Date().toLocaleString()}

`;
  
  // Add each message
  for (const message of conversation.messages) {
    const role = message.role === user ? Me : Claude;
    content += `## ${role}:
${message.content}

`;
  }
  
  // Create the entry
  try {
    const response = await fetch(`${MCP_SERVER_URL}/api/entry`, {
      method: POST,
      headers: {
        Content-Type: application/json
      },
      body: JSON.stringify({
        content,
        tags: [claude, conversation]
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      window.claudeDesktop.showNotification(Entry created in Day One!);
    } else {
      window.claudeDesktop.showNotification(Failed to create Day One entry);
    }
  } catch (error) {
    window.claudeDesktop.showNotification(`Error: ${error.message}`);
  }
}

// Register with Claude Desktop
window.claudeDesktop.registerPlugin({
  name: Day One Journal,
  description: Save conversations to Day One Journal,
  version: 1.0.0,
  actions: [
    {
      name: Save to Day One,
      description: Save this conversation to Day One Journal,
      handler: createJournalEntry
    }
  ]
});

