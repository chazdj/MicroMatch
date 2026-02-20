import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext";

/**
 * ProjectsPage displays all open projects fetched from the backend.
 * 
 * Features:
 * - Fetch projects using JWT token from AuthContext
 * - Show loading and error states
 * - Render project title, description, and required skills
 */
export default function ProjectsPage() {
  const { token } = useContext(AuthContext);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch projects from backend
    const fetchProjects = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch("http://127.0.0.1:8000/projects", {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error(`Error fetching projects: ${response.statusText}`);
        }

        const data = await response.json();
        setProjects(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, [token]);

  if (loading) return <p style={{ textAlign: "center" }}>Loading projects...</p>;
  if (error) return <p style={{ textAlign: "center", color: "red" }}>{error}</p>;

  return (
    <div style={{ maxWidth: "800px", margin: "50px auto" }}>
      <h1 style={{ textAlign: "center" }}>Open Projects</h1>
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
                marginBottom: "15px" 
              }}
            >
              <h2>{project.title}</h2>
              <p>{project.description}</p>
              {project.required_skills && (
                <p>
                  <strong>Skills Required:</strong> {project.required_skills}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}