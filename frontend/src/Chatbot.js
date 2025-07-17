import React, { useContext, useState } from "react";
import { AuthContext } from "./AuthContext";
import "./Chatbot.css";

import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  CircularProgress,
} from "@mui/material";

export default function Chatbot() {
  const { auth, logout } = useContext(AuthContext);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState("");
  const [medicines, setMedicines] = useState([]);
  const [error, setError] = useState("");

  const baseURL =
    process.env.NODE_ENV === "production"
      ? "" // Use relative URLs for same-origin requests in production
      : "http://localhost:5050"; // Local development server

  const handleSend = async () => {
    if (!message.trim()) return;

    setChat((prev) => [...prev, { sender: "user", text: message }]);
    setLoading(true);
    setResponse("");
    setMedicines([]);
    setError("");

    try {
      const res = await fetch(`${baseURL}/api/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${auth.token}`,
        },
        body: JSON.stringify({ symptoms: message.trim() })
      });

      const data = await res.json();

      if (res.ok) {
        setResponse(data.disease);
        setMedicines(data.medicines);
        setChat((prev) => [
          ...prev,
          {
            sender: "bot",
            text: `Disease: ${data.disease}\nMedicines: ${data.medicines.join(", ")}`,
          },
        ]);
      } else {
        setError(data.msg || "Prediction failed");
        setChat((prev) => [
          ...prev,
          { sender: "bot", text: data.msg || "Prediction failed" },
        ]);
      }
    } catch (err) {
      setError("Error connecting to server.");
      setChat((prev) => [
        ...prev,
        { sender: "bot", text: "Error connecting to server." },
      ]);
    }

    setMessage("");
    setLoading(false);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box display="flex" alignItems="center" gap={1}>
          <img
            src={`https://api.dicebear.com/7.x/thumbs/svg?seed=${auth.user?.username}`}
            alt="avatar"
            className="avatar"
          />
          <Typography variant="h6" className="welcome-text">
            Welcome, <span className="username">{auth.user?.username}</span>
          </Typography>
        </Box>
        <Button variant="outlined" onClick={logout}>Logout</Button>
      </Box>

      <Paper sx={{ p: 2, minHeight: 300, maxHeight: 400, overflowY: "auto", mb: 2 }}>
        {chat.map((msg, index) => (
          <Box
            key={index}
            className={`message ${msg.sender}`}
            sx={{ textAlign: msg.sender === "user" ? "right" : "left" }}
          >
            <Typography sx={{ whiteSpace: "pre-line" }}>{msg.text}</Typography>
          </Box>
        ))}

        {loading && (
          <Box display="flex" justifyContent="center" mt={2}>
            <CircularProgress />
          </Box>
        )}
      </Paper>

      <Box display="flex" gap={2}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type symptoms (e.g. fever, cough)..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSend();
          }}
          disabled={loading}
        />
        <Button
          variant="contained"
          onClick={handleSend}
          disabled={loading || !message.trim()}
        >
          {loading ? "Loading..." : "Send"}
        </Button>
      </Box>

      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}
    </Container>
  );
}
