const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());

// Helper function to execute Day One CLI commands
function executeDayOneCommand(command) {
  return new Promise((resolve, reject) => {
    exec(`dayone2 ${command}`, (error, stdout, stderr) => {
      if (error) {
        reject(`Error: ${error.message}`);
        return;
      }
      if (stderr) {
        reject(`Error: ${stderr}`);
        return;
      }
      resolve(stdout);
    });
  });
}

// Routes
app.post('/api/entry', async (req, res) => {
  try {
    const { content, tags = [], date, journal } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }
    let command = `new "${content.replace(/"/g, '\"')}"`;
    
    // Add tags if provided
    if (tags && tags.length > 0) {
      const tagString = tags.map(tag => `#${tag}`).join(' ');
      command += ` ${tagString}`;
    }
    
    // Add date if provided
    if (date) {
      command += ` --date="${date}"`;
    }
    
    // Add journal if provided
    if (journal) {
      command += ` --journal="${journal}"`;
    }
    
    const result = await executeDayOneCommand(command);
    res.json({ success: true, result });
  } catch (error) {
    console.error('Error creating entry:', error);
    res.status(500).json({ error: error.toString() });
  }
});

// Get health status
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
