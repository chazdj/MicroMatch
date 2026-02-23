import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext";

/**
 * MyApplications page
 *
 * Displays all applications submitted by the authenticated student.
 *
 * Features:
 * - Fetches applications from backend
 * - Shows status and submission date
 * - Handles loading and error states
 */
export default function MyApplications() {
  const { token } = useContext(AuthContext);

  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch student's applications
   */
  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(
          "http://127.0.0.1:8000/applications/me",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch applications");
        }

        const data = await response.json();
        setApplications(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, [token]);

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
      <h1 style={{ textAlign: "center" }}>
        My Applications
      </h1>

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
                border: "1px solid #ccc",
                borderRadius: "8px",
                padding: "15px",
                marginBottom: "15px",
              }}
            >
              <p>
                <strong>Project ID:</strong> {app.project_id}
              </p>

              <p>
                <strong>Status:</strong>{" "}
                <span
                  style={{
                    color:
                      app.status === "pending"
                        ? "orange"
                        : app.status === "accepted"
                        ? "green"
                        : app.status === "rejected"
                        ? "red"
                        : "black",
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