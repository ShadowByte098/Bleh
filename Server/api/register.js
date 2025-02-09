// pages/api/register.js
export default function handler(req, res) {
  if (req.method === 'POST') {
    // For testing, simply log the received data and return a success message.
    console.log("Received registration data:", req.body);
    // In a real implementation, you would store the data in a database.
    res.status(200).json({ success: true, received: req.body });
  } else {
    res.status(405).json({ message: 'Method Not Allowed' });
  }
}
