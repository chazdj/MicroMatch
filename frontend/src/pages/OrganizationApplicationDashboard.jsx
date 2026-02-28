import { useEffect, useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";

export default function OrganizationApplicationsDashboard() {
  const { token, user } = useContext(AuthContext);

  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [projectId] = useState(""); // You may later replace with selector

  const [page, setPage] = useState(0);
  const limit = 10;

  /**
   * Fetch applications from backend
   */
  const fetchApplications = async () => {
    try {
      setLoading(true);

      const res = await axios.get(
        `/projects/${projectId}/applications`,
        {
          params: {
            skip: page * limit,
            limit: limit
          },
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setApplications(res.data);
    } catch (error) {
      console.error("Failed loading applications", error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Accept or reject application
   */
  const updateApplicationStatus = async (applicationId, status) => {
    if (!window.confirm(`Confirm ${status}?`)) return;

    try {
      await axios.patch(
        `/applications/${applicationId}/status`,
        { status },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      await fetchApplications();
    } catch (error) {
      alert("Operation failed");
    }
  };

  useEffect(() => {
    if (projectId) fetchApplications();
  }, [projectId, page]);

  if (loading) return <div>Loading applications...</div>;

  if (!user || user.role !== "organization") {
    return <div>Access restricted to organization users.</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">
        Organization Applications Dashboard
      </h2>

      {applications.length === 0 && (
        <p className="text-gray-500">
          No applications have been submitted yet.
        </p>
      )}

      <table className="w-full border rounded-lg overflow-hidden">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-3 text-left">Student Name</th>
            <th className="p-3 text-left">Email</th>
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