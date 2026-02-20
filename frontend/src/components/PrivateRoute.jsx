import { Navigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

/**
 * Wraps a component to restrict access to authenticated users only.
 * Redirects unauthenticated users to login page.
 */
export default function PrivateRoute({ children }) {
  const { token } = useContext(AuthContext);
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}