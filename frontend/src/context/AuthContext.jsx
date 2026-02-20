import { createContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

/**
 * AuthContext provides authentication state and actions across the app.
 * - Holds the current user token and email
 * - Provides login, logout, and token persistence
 */
export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null); // JWT token
  const [email, setEmail] = useState(null); // User email
  const navigate = useNavigate();

  // Load token from localStorage when app starts
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedEmail = localStorage.getItem("email");
    if (storedToken) setToken(storedToken);
    if (storedEmail) setEmail(storedEmail);
  }, []);

  /**
   * Logs in a user
   * @param {string} token JWT token from backend
   * @param {string} email User email
   */
  const login = (token, email) => {
    setToken(token);
    setEmail(email);
    localStorage.setItem("token", token);
    localStorage.setItem("email", email);
    navigate("/"); // Redirect to home or dashboard
  };

  /**
   * Logs out a user
   */
  const logout = () => {
    setToken(null);
    setEmail(null);
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ token, email, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}