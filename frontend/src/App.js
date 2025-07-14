import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./login";
import Signup from "./signup";
import Chatbot from "./Chatbot";
import { AuthContext } from "./AuthContext";

function App() {
  const [auth, setAuth] = useState({
    isAuthenticated: false,
    token: null,
    user: null,
  });

  // Load token and user on initial load
  useEffect(() => {
    const token = localStorage.getItem("token");
    const user = localStorage.getItem("user");

    if (token && user) {
      setAuth({
        isAuthenticated: true,
        token,
        user: JSON.parse(user),
      });
    }
  }, []);

  const login = (token, user) => {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
    setAuth({
      isAuthenticated: true,
      token,
      user,
    });
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setAuth({
      isAuthenticated: false,
      token: null,
      user: null,
    });
  };

  const ProtectedRoute = ({ children }) => {
    return auth.isAuthenticated ? children : <Navigate to="/login" />;
  };

  return (
    <AuthContext.Provider value={{ auth, login, logout }}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Chatbot />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthContext.Provider>
  );
}

export default App;
