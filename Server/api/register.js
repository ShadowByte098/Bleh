// api/register.js

// Use a global variable so that if the function “stays warm” it will have some state.
// (This is only for demo purposes and may be lost between invocations on Vercel.)
let clients = global.__clients || [];
global.__clients = clients;

export default function handler(req, res) {
  if (req.method === "POST") {
    const client = req.body;
    // Use the current timestamp as an ID and registration time.
    client.id = Date.now();
    console.log("Registering client:", client);
    clients.push(client);
    res.status(200).json({ success: true, received: client });
  } else {
    res.status(405).json({ error: "Method Not Allowed" });
  }
}
