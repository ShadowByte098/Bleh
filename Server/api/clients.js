// api/clients.js

// Retrieve the global clients array.
let clients = global.__clients || [];

export default function handler(req, res) {
  res.status(200).json({ clients });
}
