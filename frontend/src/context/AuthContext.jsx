import { createContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {jwtDecode} from "jwt-decode";
/**
 * AuthContext provides authentication state and actions across the app.
 * - Holds the current user token and email
 * - Provides login, logout, and token persistence
 * - Automatically logs out if token is expired
 */
export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null); // JWT token
  const [email, setEmail] = useState(null); // User email
  const [role, setRole] = useState(null); // User role (student or organization)
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  /**
   * Checks if JWT token is expired
   */
  const isTokenExpired = (token) => {
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000 < Date.now();
    } catch (error) {
      return true; // If token is invalid, treat as expired
    }
  };

  // Load token from localStorage when app starts
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedEmail = localStorage.getItem("email");
    const storedRole = localStorage.getItem("role");

    if (storedToken && !isTokenExpired(storedToken)) {
      setToken(storedToken);
      setEmail(storedEmail);
      setRole(storedRole);
    } else {
      // If expired or invalid, clear everything
      localStorage.removeItem("token");
      localStorage.removeItem("email");
      localStorage.removeItem("role");
    }

    setLoading(false);
  }, []);

  /**
   * Automatically logout if token becomes expired
   */
  useEffect(() => {
    if (!token) return;

    try {
      const decoded = jwtDecode(token);
      const expirationTime = decoded.exp * 1000;
      const currentTime = Date.now();
      const timeLeft = expirationTime - currentTime;

      if (timeLeft <= 0) {
        logout();
        return;
      }

      const timer = setTimeout(() => {
        logout();
      }, timeLeft);

      return () => clearTimeout(timer);

    } catch (error) {
      logout();
    }
  }, [token]);

  /**
   * Logs in a user
   */
  const login = (token, email, role) => {
    setToken(token);
    setEmail(email);
    setRole(role);
    localStorage.setItem("token", token);
    localStorage.setItem("email", email);
    localStorage.setItem("role", role);
    navigate("/"); // Redirect to home or dashboard
  };

  /**
   * Logs out a user
   */
  const logout = () => {
    setToken(null);
    setEmail(null);
    setRole(null);
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    localStorage.removeItem("role");
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ token, email, role, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}