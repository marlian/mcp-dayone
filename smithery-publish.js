// Smithery publish script
const fs = require(fs);
const path = require(path);
const { execSync } = require(child_process);

// Configuration
const config = {
  name: mcp-dayone,
  version: 1.0.0,
  description: MCP server for Day One Journal integration with Claude Desktop,
  smitheryUrl: https://smithery.ai
};

// Files to include in the package
const filesToInclude = [
  package.json,
  server.js,
  README.md,
  .env.example,
  install.sh,
  test.js,
  claude-desktop.js,
  smithery.toml
];

// Create the package
function createPackage() {
  console.log(`Creating package for ${config.name} v${config.version}...`);
  
  // Create a temp directory
  const tempDir = path.join(__dirname, dist);
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir);
  }
  
  // Copy files
  filesToInclude.forEach(file => {
    if (fs.existsSync(path.join(__dirname, file))) {
      fs.copyFileSync(
        path.join(__dirname, file),
        path.join(tempDir, file)
      );
      console.log(`Copied ${file}`);
    } else {
      console.warn(`Warning: ${file} not found, skipping`);
    }
  });
  
  // Create archive
  const archiveName = `${config.name}-${config.version}.zip`;
  console.log(`Creating archive ${archiveName}...`);
  
  try {
    execSync(`cd ${tempDir} && zip -r ../${archiveName} .`);
    console.log(`✅ Package created: ${archiveName}`);
    console.log(`You can now upload this package to ${config.smitheryUrl}`);
  } catch (error) {
    console.error(`❌ Failed to create archive: ${error.message}`);
  }
}

// Run the publish process
createPackage();

