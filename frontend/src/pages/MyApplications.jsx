import { useState, useEffect } from "react";
import api from "../api/api";
import FeedbackForm from "../components/FeedbackForm";

/**
 * MyApplications page
 *
 * Displays all applications submitted by the authenticated student.
 *
 * Features:
 * - Fetches applications from backend
 * - Auto refreshes every 10 seconds
 * - Color coded status badges
 * - Deliverable submission for accepted applications
 * - Feedback form for completed projects
 * - Loading and error handling
 */
export default function MyApplications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Deliverable state (per application)
  const [deliverables, setDeliverables] = useState({});
  const [submitting, setSubmitting] = useState({});
  const [messages, setMessages] = useState({});

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
        err.response?.data?.detail || "Failed to fetch applications"
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
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // ----------------------------
  // Submit Deliverable
  // ----------------------------
  const handleSubmitDeliverable = async (applicationId) => {
    const content = deliverables[applicationId];
    if (!content || !content.trim()) {
      setMessages((prev) => ({
        ...prev,
        [applicationId]: { type: "error", text: "Content cannot be empty" },
      }));
      return;
    }

    try {
      setSubmitting((prev) => ({ ...prev, [applicationId]: true }));
      await api.post(`/applications/${applicationId}/deliverables`, {
        content,
      });
      setMessages((prev) => ({
        ...prev,
        [applicationId]: { type: "success", text: "Deliverable submitted!" },
      }));
    } catch (err) {
      setMessages((prev) => ({
        ...prev,
        [applicationId]: {
          type: "error",
          text: err.response?.data?.detail || "Submission failed",
        },
      }));
    } finally {
      setSubmitting((prev) => ({ ...prev, [applicationId]: false }));
    }
  };

  /**
   * Status badge colors
   */
  const getStatusStyle = (status) => {
    switch (status) {
      case "pending":
        return { backgroundColor: "#facc15", color: "#000" };
      case "accepted":
        return { backgroundColor: "#22c55e", color: "#fff" };
      case "rejected":
        return { backgroundColor: "#ef4444", color: "#fff" };
      default:
        return {};
    }
  };

  if (loading) return <p style={{ textAlign: "center" }}>Loading applications...</p>;
  if (error) return <p style={{ textAlign: "center", color: "red" }}>{error}</p>;

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
                boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
              }}
            >
              <p>
                <strong>Project:</strong>{" "}
                {app.project?.title || "Unknown Project"}
              </p>
              <p>
                <strong>Status:</strong>{" "}
                <span
                  style={{
                    ...getStatusStyle(app.status),
                    padding: "4px 10px",
                    borderRadius: "6px",
                    fontWeight: "bold",
                    textTransform: "capitalize",
                  }}
                >
                  {app.status}
                </span>
              </p>

              {/* ----------------------------
                  Deliverable Section
              ---------------------------- */}
              {app.status === "accepted" && app.project?.status !== "completed" && (
                <div style={{ marginTop: "15px" }}>
                  <h4>Submit Deliverable</h4>
                  <textarea
                    placeholder="Paste link, text, or file reference..."
                    value={deliverables[app.id] || ""}
                    onChange={(e) =>
                      setDeliverables((prev) => ({
                        ...prev,
                        [app.id]: e.target.value,
                      }))
                    }
                    style={{
                      width: "100%",
                      padding: "10px",
                      borderRadius: "6px",
                      border: "1px solid #ccc",
                      marginBottom: "10px",
                    }}
                  />
                  <button
                    onClick={() => handleSubmitDeliverable(app.id)}
                    disabled={submitting[app.id]}
                    style={{
                      padding: "8px 14px",
                      backgroundColor: "#4f46e5",
                      color: "white",
                      borderRadius: "6px",
                      cursor: "pointer",
                      opacity: submitting[app.id] ? 0.6 : 1,
                    }}
                  >
                    {submitting[app.id] ? "Submitting..." : "Submit Deliverable"}
                  </button>

                  {messages[app.id] && (
                    <p
                      style={{
                        marginTop: "8px",
                        color: messages[app.id].type === "error" ? "red" : "green",
                      }}
                    >
                      {messages[app.id].text}
                    </p>
                  )}
                </div>
              )}

              {/* ----------------------------
                  Feedback Section
                  Only shown when project is completed
              ---------------------------- */}
              {app.project?.status === "completed" && (
                <div style={{ marginTop: "15px" }}>
                  <p
                    style={{
                      display: "inline-block",
                      backgroundColor: "#dcfce7",
                      color: "#15803d",
                      padding: "4px 10px",
                      borderRadius: "6px",
                      fontWeight: "bold",
                      fontSize: "0.85rem",
                      marginBottom: "10px",
                    }}
                  >
                    ✓ Project Completed
                  </p>
                  <FeedbackForm projectId={app.project_id} />
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}