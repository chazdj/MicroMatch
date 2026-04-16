import { createContext, useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {jwtDecode} from "jwt-decode";
import api from "../api/api";

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
  const [name, setName] = useState(null);
  const [loading, setLoading] = useState(true);
  const [profileComplete, setProfileComplete] = useState(null);

  const navigate = useNavigate();
  const profileChecked = useRef(false); // To prevent multiple profile checks on re-render

  /**
   * Checks if JWT token is expired
   */
  const isTokenExpired = (token) => {
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000 < Date.now();
    } catch {
    // } catch (error) {
      return true; // If token is invalid, treat as expired
    }
  };

  /**
  * Check whether profile exists
  * Called after login and on mount if already logged in
  */
  const checkProfileComplete = useCallback(async (userRole) => {
    try {
      if (userRole === "student") {
        await api.get("/student/profile");
      } else if (userRole === "organization") {
        await api.get("/organization/profile");
      } else {
        // Admins don't have profiles
        setProfileComplete(true);
        return;
      }
      setProfileComplete(true);
    } catch (err) {
      if (err.response?.status === 404) {
        setProfileComplete(false);
      } else {
        // Network error etc — don't block the user
        setProfileComplete(true);
      }
    }
  }, []);

  // Load token from localStorage when app starts
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedEmail = localStorage.getItem("email");
    const storedRole = localStorage.getItem("role");
    const storedName = localStorage.getItem("name");

    if (storedToken && !isTokenExpired(storedToken)) {
      setToken(storedToken);
      setEmail(storedEmail);
      setRole(storedRole);
      setName(storedName);
    } else {
      // If expired or invalid, clear everything
      localStorage.removeItem("token");
      localStorage.removeItem("email");
      localStorage.removeItem("role");
      localStorage.removeItem("name");
    }

    setLoading(false);
  }, []);

  // Once role is known, check profile completeness
  useEffect(() => {
    if (role && token && !profileChecked.current) {
      profileChecked.current = true; // Prevent multiple checks
      checkProfileComplete(role);
    }
  }, [role, token, checkProfileComplete]);

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
  const login = (token, email, role, name) => {
    setToken(token);
    setEmail(email);
    setRole(role);
    setName(name);
    localStorage.setItem("token", token);
    localStorage.setItem("email", email);
    localStorage.setItem("role", role);
    localStorage.setItem("name", name ?? "");
    navigate("/"); // Redirect to home or dashboard
  };

  /**
   * Logs out a user
   */
  const logout = () => {
    setToken(null);
    setEmail(null);
    setRole(null);
    setName(null);
    setProfileComplete(null);
    profileChecked.current = false;
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    localStorage.removeItem("role");
    localStorage.removeItem("name");
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ token, email, role, name, login, logout, loading, profileComplete, setProfileComplete, checkProfileComplete}}>
      {children}
    </AuthContext.Provider>
  );
}