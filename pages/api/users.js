// pages/api/users.js
export default function handler(req, res) {
  // Dummy user data
  const users = [
    { id: 1, name: "Alice", lat: 37.7749, lng: -122.4194 },
    { id: 2, name: "Bob", lat: 51.5074, lng: -0.1278 },
    { id: 3, name: "Charlie", lat: 35.6895, lng: 139.6917 }
  ];
  
  res.status(200).json({ users });
}
