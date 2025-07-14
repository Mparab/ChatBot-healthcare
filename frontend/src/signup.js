import React, { useState, useContext } from "react";
import { TextField, Button, Container, Typography, Box } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (res.status === 201) {
        navigate("/login");
      } else {
        setError(data.msg || "Signup failed");
      }
    } catch (err) {
      setError("Network error");
    }
  };

  return (
    <Container maxWidth="xs">
      <Box sx={{ mt: 8 }}>
        <Typography variant="h5" align="center">Sign Up</Typography>
        <form onSubmit={handleSignup}>
          <TextField label="Username" fullWidth margin="normal" value={username} onChange={e => setUsername(e.target.value)} required />
          <TextField label="Password" fullWidth margin="normal" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          <Button type="submit" fullWidth variant="contained" sx={{ mt: 2 }}>Sign Up</Button>
        </form>
        {error && <Typography color="error" align="center">{error}</Typography>}
      </Box>
    </Container>
  );
}
