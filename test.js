const http = require(http);

const testEntry = {
  content: Test entry from MCP server,
  tags: [test, mcp],
  date: new Date().toISOString()
};

const options = {
  hostname: localhost,
  port: 3000,
  path: /api/entry,
  method: POST,
  headers: {
    Content-Type: application/json
  }
};

console.log(Testing MCP-DayOne server...);
console.log(`Sending test entry: ${JSON.stringify(testEntry, null, 2)}`);

const req = http.request(options, (res) => {
  let data = ;
  
  res.on(data, (chunk) => {
    data += chunk;
  });
  
  res.on(end, () => {
    console.log(`Status: ${res.statusCode}`);
    
    try {
      const result = JSON.parse(data);
      console.log(Response:);
      console.log(JSON.stringify(result, null, 2));
      
      if (result.success) {
        console.log(✅ Test passed: Entry created successfully!);
      } else {
        console.log(❌ Test failed: Could not create entry.);
      }
    } catch (e) {
      console.log(Raw response:, data);
      console.log(❌ Test failed: Invalid JSON response.);
    }
  });
});

req.on(error, (e) => {
  console.error(`❌ Test failed: ${e.message}`);
});

req.write(JSON.stringify(testEntry));
req.end();

