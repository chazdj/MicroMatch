import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../api/api";

export default function OrgDeliverablesDashboard() {
  const { token, role } = useContext(AuthContext);

  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [deliverables, setDeliverables] = useState([]);
  const [loading, setLoading] = useState(false);

  // ----------------------------
  // Fetch org projects
  // ----------------------------
  const fetchProjects = async () => {
    try {
      const res = await api.get("/projects/me");
      setProjects(res.data);

      if (res.data.length > 0) {
        setSelectedProjectId(res.data[0].id);
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

      const res = await api.get(
        `/projects/${selectedProjectId}/deliverables`
      );

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
      await api.put(`/deliverables/${id}/review`, {
        status,
      });

      fetchDeliverables();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
        "Failed to review deliverable"
      );
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    fetchDeliverables();
  }, [selectedProjectId]);

  if (role !== "organization") {
    return <div>Access restricted</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">
        Deliverables Dashboard
      </h2>

      {/* Project Selector */}
      <div className="mb-6">
        <label className="block font-medium mb-2">
          Select Project
        </label>

        <select
          value={selectedProjectId || ""}
          onChange={(e) =>
            setSelectedProjectId(e.target.value)
          }
          className="border px-4 py-2 rounded w-full max-w-md"
        >
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.title}
            </option>
          ))}
        </select>
      </div>

      {/* Loading */}
      {loading && <div>Loading deliverables...</div>}

      {/* Empty */}
      {!loading && deliverables.length === 0 && (
        <p className="text-gray-500">
          No deliverables submitted yet.
        </p>
      )}

      {/* Table */}
      {!loading && deliverables.length > 0 && (
        <table className="w-full border rounded-lg overflow-hidden">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 text-left">Student</th>
              <th className="p-3 text-left">Content</th>
              <th className="p-3 text-left">Status</th>
              <th className="p-3 text-left">Actions</th>
            </tr>
          </thead>

          <tbody>
            {deliverables.map((d) => (
              <tr key={d.id} className="border-t">
                <td className="p-3">
                  {d.student?.email}
                </td>

                <td className="p-3">
                  {d.content || "No content"}
                </td>

                <td className="p-3">
                  <span
                    className={`px-3 py-1 rounded text-white text-sm ${
                      d.status === "submitted"
                        ? "bg-yellow-500"
                        : d.status === "accepted"
                        ? "bg-green-600"
                        : "bg-red-600"
                    }`}
                  >
                    {d.status}
                  </span>
                </td>

                <td className="p-3 space-x-2">
                  {d.status === "submitted" && (
                    <>
                      <button
                        className="px-3 py-1 bg-green-600 text-white rounded"
                        onClick={() =>
                          reviewDeliverable(d.id, "accepted")
                        }
                      >
                        Accept
                      </button>

                      <button
                        className="px-3 py-1 bg-red-600 text-white rounded"
                        onClick={() =>
                          reviewDeliverable(d.id, "rejected")
                        }
                      >
                        Reject
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}