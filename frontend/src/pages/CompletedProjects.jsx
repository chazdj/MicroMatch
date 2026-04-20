import { useEffect, useState } from "react";
import api from "../api/api";
import { Link } from "react-router-dom";

export default function CompletedProjects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/projects/me")
      .then(res => setProjects(res.data.filter(p => p.status === "completed")))
      .catch(() => setError("Failed to load completed projects"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="p-6">Loading...</p>;
  if (error) return <p className="p-6 text-red-500">{error}</p>;

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Completed Projects</h1>
      {projects.length === 0 ? (
        <p className="text-gray-500">No completed projects yet.</p>
      ) : (
        <ul className="space-y-4">
          {projects.map(project => (
            <li key={project.id} className="border rounded-lg p-4 shadow-sm">
              <h2 className="text-lg font-semibold">{project.title}</h2>
              <p className="text-sm text-gray-600">{project.description}</p>
              <span className="inline-block mt-2 px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                ✓ Completed
              </span>
              <div className="mt-3">
                
                <Link to="/my-applications" className="text-primary text-sm underline">
                  View Applications & Leave Feedback →
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}