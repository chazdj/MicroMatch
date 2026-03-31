import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../api/api";

export default function OrgDeliverablesDashboard() {
  const { token, role } = useContext(AuthContext);
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [deliverables, setDeliverables] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);

  // ----------------------------
  // Fetch org projects
  // ----------------------------
  const fetchProjects = async () => {
    try {
      const res = await api.get("/projects/me");
      setProjects(res.data);
      if (res.data.length > 0) {
        setSelectedProjectId(res.data[0].id);
        setSelectedProject(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to fetch projects", err);
    }
  };

  // ----------------------------
  // Fetch deliverables
  // ----------------------------
  const fetchDeliverables = async () => {
    if (!selectedProjectId) return;
    try {
      setLoading(true);
      const res = await api.get(`/deliverables/projects/${selectedProjectId}`);
      setDeliverables(res.data);
    } catch (err) {
      console.error("Failed to fetch deliverables", err);
    } finally {
      setLoading(false);
    }
  };

  // ----------------------------
  // Review deliverable
  // ----------------------------
  const reviewDeliverable = async (id, status) => {
    if (!window.confirm(`Confirm ${status}?`)) return;
    try {
      await api.put(`/deliverables/${id}/review`, { status });
      fetchDeliverables();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to review deliverable");
    }
  };

  // ----------------------------
  // Mark project complete
  // ----------------------------
  const handleMarkComplete = async () => {
    if (!window.confirm("Mark this project as complete? This cannot be undone.")) return;
    try {
      await api.put(`/projects/${selectedProjectId}/complete`);
      alert("Project marked as complete!");
      fetchProjects();
    } catch (err) {
      alert(err.response?.data?.detail || "Could not complete project");
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      const found = projects.find((p) => p.id === parseInt(selectedProjectId));
      setSelectedProject(found || null);
      fetchDeliverables();
    }
  }, [selectedProjectId]);

  if (role !== "organization") {
    return <div>Access restricted</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-800">
          Deliverables Dashboard
        </h2>
        <p className="text-gray-500">
          Review student submissions for your projects
        </p>
      </div>

      {/* Project Selector */}
      <div className="bg-white p-5 rounded-2xl shadow-sm border border-primaryPale">
        <label className="block text-sm font-medium mb-2 text-gray-600">
          Select Project
        </label>
        <select
          value={selectedProjectId || ""}
          onChange={(e) => setSelectedProjectId(e.target.value)}
          className="border border-gray-200 px-4 py-2 rounded-lg w-full max-w-md focus:ring-2 focus:ring-primary"
        >
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.title} {p.status === "completed" ? "✓ Completed" : ""}
            </option>
          ))}
        </select>

        {/* Mark Project Complete button — only shown if project is not already completed */}
        {selectedProject && selectedProject.status !== "completed" && (
          <button
            onClick={handleMarkComplete}
            className="mt-3 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium"
          >
            Mark Project Complete
          </button>
        )}

        {/* Completed badge */}
        {selectedProject?.status === "completed" && (
          <p className="mt-3 inline-block px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
            ✓ This project has been marked complete
          </p>
        )}
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-gray-500">Loading deliverables...</div>
      )}

      {/* Empty */}
      {!loading && deliverables.length === 0 && (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-primaryPale text-center text-gray-500">
          No deliverables submitted yet.
        </div>
      )}

      {/* Deliverable Cards */}
      <div className="grid gap-5">
        {deliverables.map((d) => (
          <div
            key={d.id}
            className="bg-white p-6 rounded-2xl shadow-sm border border-primaryPale"
          >
            {/* Top Row */}
            <div className="flex justify-between items-center mb-3">
              <div>
                <p className="text-sm text-gray-500">Student</p>
                <p className="font-semibold">
                  {d.student?.email || "Unknown"}
                </p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  d.status === "submitted"
                    ? "bg-yellow-100 text-yellow-700"
                    : d.status === "accepted"
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-700"
                }`}
              >
                {d.status}
              </span>
            </div>

            {/* Content */}
            <div className="mb-4">
              <p className="text-sm text-gray-500 mb-1">Submission</p>
              <p className="text-gray-700 whitespace-pre-wrap">{d.content}</p>
            </div>

            {/* Review Actions — only if project not yet completed */}
            {d.status === "submitted" && selectedProject?.status !== "completed" && (
              <div className="flex gap-3">
                <button
                  onClick={() => reviewDeliverable(d.id, "accepted")}
                  className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primaryLight transition"
                >
                  Accept
                </button>
                <button
                  onClick={() => reviewDeliverable(d.id, "rejected")}
                  className="bg-gray-200 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
                >
                  Reject
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}