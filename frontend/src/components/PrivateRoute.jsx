import { Navigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

/**
 * Wraps a component to restrict access to authenticated users only.
 * Redirects unauthenticated users to login page.
 * Now supports role-based access control by checking user role.
 */
export default function PrivateRoute({ children, allowedRoles }) {
  const { token, role, loading } = useContext(AuthContext);

  if (loading) {
    return null;
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}