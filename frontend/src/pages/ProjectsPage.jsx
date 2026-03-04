import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../api/api";

/**
 * ProjectsPage displays all open projects fetched from the backend.
 *
 * Features:
 * - Fetch projects using JWT token from AuthContext
 * - Allows students to apply to a project
 * - Displays loading and error states
 */
export default function ProjectsPage() {
  const { token } = useContext(AuthContext);

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [applyingProjectId, setApplyingProjectId] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");

  /**
   * Fetch open projects from backend
   */
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await api.get("/projects");

        setProjects(response.data);

      } catch (err) {
        setError(
          err.response?.data?.detail ||
          "Error fetching projects"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  /**
   * Handles applying to a project.
   *
   * @param {number} projectId - ID of the project being applied to
   */
  const handleApply = async (projectId) => {
    try {
      setApplyingProjectId(projectId);
      setError(null);
      setSuccessMessage("");

      await api.post("/applications", {
        project_id: projectId,
      });

      setSuccessMessage("Application submitted successfully!");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to apply"
      );
    } finally {
      setApplyingProjectId(null);
    }
  };

  if (loading)
    return <p style={{ textAlign: "center" }}>Loading projects...</p>;

  if (error)
    return <p style={{ textAlign: "center", color: "red" }}>{error}</p>;

  return (
    <div style={{ maxWidth: "800px", margin: "50px auto" }}>
      <h1 style={{ textAlign: "center" }}>Open Projects</h1>

      {successMessage && (
        <p style={{ textAlign: "center", color: "green" }}>
          {successMessage}
        </p>
      )}

      {projects.length === 0 ? (
        <p>No projects found.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {projects.map((project) => (
            <li
              key={project.id}
              style={{
                border: "1px solid #ccc",
                borderRadius: "8px",
                padding: "15px",
                marginBottom: "15px",
              }}
            >
              <h2>{project.title}</h2>
              <p>{project.description}</p>

              {project.required_skills && (
                <p>
                  <strong>Skills Required:</strong>{" "}
                  {project.required_skills}
                </p>
              )}

              {/* Apply Button */}
              <button
                onClick={() => handleApply(project.id)}
                disabled={applyingProjectId === project.id}
                style={{
                  marginTop: "10px",
                  padding: "8px 12px",
                  cursor:
                    applyingProjectId === project.id
                      ? "not-allowed"
                      : "pointer",
                }}
              >
                {applyingProjectId === project.id
                  ? "Applying..."
                  : "Apply"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}