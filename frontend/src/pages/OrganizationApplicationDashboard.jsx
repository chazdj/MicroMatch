import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../api/api";

export default function OrganizationApplicationsDashboard() {
  const { token, role } = useContext(AuthContext);

  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(false);

  const [page, setPage] = useState(0);
  const limit = 10;

  // ----------------------------
  // Fetch organization projects
  // ----------------------------
  const fetchProjects = async () => {
    try {
      const res = await api.get("/projects/me", {
        headers: { Authorization: `Bearer ${token}` },
      });

      setProjects(res.data);

      if (res.data.length > 0) {
        setSelectedProjectId(res.data[0].id);
      }

    } catch (error) {
      console.error("Failed loading projects", error);
    }
  };

  // ----------------------------
  // Fetch applications for project
  // ----------------------------
  const fetchApplications = async () => {
    if (!selectedProjectId) return;

    try {
      setLoading(true);

      const res = await api.get(`/projects/${selectedProjectId}/applications`,
        {
          params: {
            skip: page * limit,
            limit: limit,
          },
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setApplications(res.data);

    } catch (error) {
      console.error("Failed loading applications", error);
    } finally {
      setLoading(false);
    }
  };

  // ----------------------------
  // Update status
  // ----------------------------
  const updateApplicationStatus = async (applicationId, status) => {
    if (!window.confirm(`Confirm ${status}?`)) return;

    try {
      await api.patch(`/applications/${applicationId}/status`,
        { status },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      fetchApplications();

    } catch (error) {
      alert("Operation failed");
    }
  };

  useEffect(() => {
    fetchProjects();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchApplications();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProjectId, page]);

  if (role !== "organization") {
    return <div>Access restricted to organization users.</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">
        Applications Dashboard
      </h2>

      {/* Project Selector */}
      <div className="mb-6">
        <label className="block font-medium mb-2">
          Select Project
        </label>

        <select
          value={selectedProjectId || ""}
          onChange={(e) => {
            setSelectedProjectId(e.target.value);
            setPage(0);
          }}
          className="border px-4 py-2 rounded w-full max-w-md"
        >
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.title}
            </option>
          ))}
        </select>
      </div>

      {loading && <div>Loading applications...</div>}

      {!loading && applications.length === 0 && (
        <p className="text-gray-500">
          No applications for this project yet.
        </p>
      )}

      {!loading && applications.length > 0 && (
        <table className="w-full border rounded-lg overflow-hidden">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 text-left">Student Email</th>
              <th className="p-3 text-left">University</th>
              <th className="p-3 text-left">Status</th>
              <th className="p-3 text-left">Actions</th>
            </tr>
          </thead>

          <tbody>
            {applications.map((app) => {
              const profile = app.student?.student_profile;

              return (
                <tr key={app.id} className="border-t">
                  <td className="p-3">
                    {app.student?.email}
                  </td>

                  <td className="p-3">
                    {profile?.university || "N/A"}
                  </td>

                  <td className="p-3">
                    <span
                      className={`px-3 py-1 rounded text-white text-sm ${
                        app.status === "pending"
                          ? "bg-yellow-500"
                          : app.status === "accepted"
                          ? "bg-green-600"
                          : "bg-red-600"
                      }`}
                    >
                      {app.status}
                    </span>
                  </td>

                  <td className="p-3 space-x-2">
                    {app.status === "pending" && (
                      <>
                        <button
                          className="px-3 py-1 bg-green-600 text-white rounded"
                          onClick={() =>
                            updateApplicationStatus(app.id, "accepted")
                          }
                        >
                          Accept
                        </button>

                        <button
                          className="px-3 py-1 bg-red-600 text-white rounded"
                          onClick={() =>
                            updateApplicationStatus(app.id, "rejected")
                          }
                        >
                          Reject
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      <div className="mt-6 flex justify-between">
        <button
          disabled={page === 0}
          onClick={() => setPage(page - 1)}
          className="px-4 py-2 border rounded disabled:opacity-50"
        >
          Previous
        </button>

        <button
          onClick={() => setPage(page + 1)}
          className="px-4 py-2 border rounded"
        >
          Next
        </button>
      </div>
    </div>
  );
}