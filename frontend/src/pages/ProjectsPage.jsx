import { useState, useEffect } from "react";
import api from "../api/api";

/**
 * ProjectsPage displays all open projects fetched from the backend.
 *
 * Features:
 * - Fetch projects using JWT token from AuthContext
 * - Client-side search: filters by title, description, and required_skills
 * - Allows students to apply to a project
 * - Displays loading and error states
 */
export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [applyingProjectId, setApplyingProjectId] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

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

  /**
   * Filters the full project list against the current search query.
   * Matches against title, description, and required_skills (case-insensitive).
   */
  const filteredProjects = projects.filter((project) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      project.title?.toLowerCase().includes(q) ||
      project.description?.toLowerCase().includes(q) ||
      project.required_skills?.toLowerCase().includes(q)
    );
  });

  if (loading)
    return <p style={{ textAlign: "center" }}>Loading projects...</p>;

  if (error)
    return <p style={{ textAlign: "center", color: "red" }}>{error}</p>;

  return (
    <div style={{ maxWidth: "800px", margin: "50px auto" }}>
      <h1 style={{ textAlign: "center" }}>Open Projects</h1>

      {/* Search Bar */}
      <div style={{ margin: "20px 0" }}>
        <input
          type="text"
          placeholder="Search by title, description, or skills…"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: "100%",
            padding: "10px 14px",
            fontSize: "15px",
            border: "1.5px solid #ccc",
            borderRadius: "8px",
            outline: "none",
            boxSizing: "border-box",
            transition: "border-color 0.2s",
          }}
          onFocus={(e) => (e.target.style.borderColor = "#fe8997")}
          onBlur={(e) => (e.target.style.borderColor = "#ccc")}
        />
        {searchQuery && (
          <p style={{ marginTop: "6px", fontSize: "13px", color: "#888" }}>
            {filteredProjects.length === 0
              ? "No projects match your search."
              : `${filteredProjects.length} project${filteredProjects.length !== 1 ? "s" : ""} found`}
          </p>
        )}
      </div>

      {successMessage && (
        <p style={{ textAlign: "center", color: "green" }}>
          {successMessage}
        </p>
      )}

      {filteredProjects.length === 0 && !searchQuery ? (
        <p>No projects found.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {filteredProjects.map((project) => (
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
                {applyingProjectId === project.id ? "Applying..." : "Apply"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}