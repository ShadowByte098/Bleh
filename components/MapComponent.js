// components/MapComponent.js
import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix default icon issues with Next.js and Leaflet.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png'
});

export default function MapComponent() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // Fetch the dummy user data from our API endpoint.
    fetch('/api/users')
      .then((res) => res.json())
      .then((data) => setUsers(data.users))
      .catch((err) => console.error("Error fetching user data:", err));
  }, []);

  return (
    <MapContainer center={[20, 0]} zoom={2} style={{ height: "80vh", width: "100%" }}>
      <TileLayer
        attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {users.map((user) => (
        <Marker key={user.id} position={[user.lat, user.lng]}>
          <Popup>
            <div>
              <strong>{user.name}</strong>
              <br />
              <button onClick={() => alert(`Sending command to ${user.name}`)}>
                Send Command
              </button>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
