import React from "react";
import { useEffect, useState } from "react";
import axios from "axios";
import { io } from "socket.io-client";

// Socket.IO korrekt initialisieren
const socket = io({
  path: "/socket.io",
  transports: ["websocket"],
  withCredentials: false,
});

export default function App() {
  const [email, setEmail] = useState(null);
  const [inbox, setInbox] = useState([]);

  // E-Mail-Adresse vom Backend holen und abonnieren
  useEffect(() => {
    const fetchEmail = async () => {
      try {
        const res = await axios.get("/api/new-email");
        setEmail(res.data.email);
        socket.emit("subscribe", { email: res.data.email });
      } catch (err) {
        console.error("Fehler beim Abrufen der Email:", err);
      }
    };
    fetchEmail();
  }, []);

  // E-Mails empfangen
  useEffect(() => {
    socket.on("inbox", (messages) => {
      setInbox((prev) => [...prev, ...messages]);
    });
    return () => socket.off("inbox");
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "monospace", maxWidth: "800px", margin: "0 auto" }}>
      <h1>📨 Deine temporäre E-Mail</h1>
      {email ? <h2>{email}</h2> : <p>Wird geladen...</p>}

      <h3>📥 Posteingang:</h3>
      {inbox.length === 0 && <p>Noch keine E-Mails.</p>}
      <ul>
        {inbox.map((msg, i) => (
          <li
            key={i}
            style={{
              border: "1px solid #ccc",
              borderRadius: "8px",
              marginBottom: "1rem",
              padding: "1rem",
              background: "#f9f9f9",
            }}
          >
            <strong>Betreff: {msg.subject || "(kein Betreff)"}</strong>
            <p style={{ whiteSpace: "pre-wrap" }}>{msg.body || "(kein Inhalt)"}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

