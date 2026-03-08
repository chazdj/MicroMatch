import { useState, useEffect } from "react";
import api from "../api/api";

/**
 * MyApplications page
 *
 * Displays all applications submitted by the authenticated student.
 *
 * Features:
 * - Fetches applications from backend
 * - Auto refreshes every 10 seconds
 * - Color coded status badges
 * - Loading and error handling
 */

export default function MyApplications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch student's applications
   */
  const fetchApplications = async () => {
    try {
      setError(null);

      const response = await api.get("/applications/me");

      setApplications(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to fetch applications"
      );
    } finally {
      setLoading(false);
    }
  };

  /**
   * Initial fetch + polling for real-time updates
   */
  useEffect(() => {
    fetchApplications();

    const interval = setInterval(() => {
      fetchApplications();
    }, 10000); // refresh every 10 seconds

    return () => clearInterval(interval);
  }, []);

  /**
   * Status badge colors
   */
  const getStatusStyle = (status) => {
    switch (status) {
      case "pending":
        return {
          backgroundColor: "#facc15",
          color: "#000",
        };
      case "accepted":
        return {
          backgroundColor: "#22c55e",
          color: "#fff",
        };
      case "rejected":
        return {
          backgroundColor: "#ef4444",
          color: "#fff",
        };
      default:
        return {};
    }
  };

  if (loading)
    return <p style={{ textAlign: "center" }}>Loading applications...</p>;

  if (error)
    return (
      <p style={{ textAlign: "center", color: "red" }}>
        {error}
      </p>
    );

  return (
    <div style={{ maxWidth: "800px", margin: "50px auto" }}>
      <h1 style={{ textAlign: "center" }}>My Applications</h1>

      {applications.length === 0 ? (
        <p style={{ textAlign: "center" }}>
          You have not applied to any projects yet.
        </p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {applications.map((app) => (
            <li
              key={app.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "10px",
                padding: "18px",
                marginBottom: "15px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.05)"
              }}
            >
              <p>
                <strong>Project:</strong> {app.project?.title || "Unknown Project"}
              </p>

              <p>
                <strong>Project ID:</strong> {app.project_id}
              </p>

              <p>
                <strong>Status:</strong>{" "}
                <span
                  style={{
                    ...getStatusStyle(app.status),
                    padding: "4px 10px",
                    borderRadius: "6px",
                    fontWeight: "bold",
                    textTransform: "capitalize"
                  }}
                >
                  {app.status}
                </span>
              </p>

              <p>
                <strong>Applied On:</strong>{" "}
                {new Date(app.created_at).toLocaleString()}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}