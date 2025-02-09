// server.js
const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const port = process.env.PORT || 3000;

// Parse JSON bodies
app.use(bodyParser.json());

// In-memory store for registered clients
let clients = [];

// Endpoint to register a new client
app.post('/register', (req, res) => {
  const client = req.body;
  // For simplicity, add a timestamp and an ID
  client.id = Date.now();
  console.log("Registering client:", client);
  clients.push(client);
  res.status(200).json({ success: true });
});

// Endpoint to get all registered clients
app.get('/clients', (req, res) => {
  res.json({ clients });
});

// Serve static files from the "public" folder
app.use(express.static('public'));

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});