import { useState, useEffect } from "react";
import api from "../api/api";

export default function AdminModerationDashboard() {
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("users");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [usersRes, projectsRes] = await Promise.all([
        api.get("/admin/users"),
        api.get("/admin/projects"),
      ]);
      setUsers(usersRes.data);
      setProjects(projectsRes.data);
    } catch (err) {
      console.error("Failed to load admin data", err);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (userId, currentStatus) => {
    try {
      await api.put(`/admin/users/${userId}/status?is_active=${!currentStatus}`);
      setUsers((prev) =>
        prev.map((u) =>
          u.id === userId ? { ...u, is_active: !currentStatus } : u
        )
      );
    } catch (err) {
      console.error("Failed to update user status", err);
    }
  };

  const disableProject = async (projectId) => {
    try {
      await api.delete(`/admin/listings/${projectId}`);
      setProjects((prev) =>
        prev.map((p) =>
          p.id === projectId ? { ...p, status: "disabled" } : p
        )
      );
    } catch (err) {
      console.error("Failed to disable project", err);
    }
  };

  if (loading)
    return <p className="text-center text-gray-500 mt-10">Loading...</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Admin Moderation</h1>
        <p className="text-gray-500 text-sm mt-1">
          Manage users and project listings
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab("users")}
          className={`px-6 py-3 text-sm font-medium transition ${
            activeTab === "users"
              ? "border-b-2 border-primary text-primary"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Users ({users.length})
        </button>
        <button
          onClick={() => setActiveTab("projects")}
          className={`px-6 py-3 text-sm font-medium transition ${
            activeTab === "projects"
              ? "border-b-2 border-primary text-primary"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Projects ({projects.length})
        </button>
      </div>

      {/* Users Tab */}
      {activeTab === "users" && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-gray-600 text-left border-b text-xs uppercase tracking-wide">
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50 transition">
                    <td className="px-4 py-3 text-gray-400">{user.id}</td>
                    <td className="px-4 py-3 text-gray-800">{user.email}</td>
                    <td className="px-4 py-3 capitalize text-gray-600">
                      {user.role}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`text-xs font-semibold px-2 py-1 rounded ${
                          user.is_active
                            ? "text-green-700 bg-green-50"
                            : "text-red-700 bg-red-50"
                        }`}
                      >
                        {user.is_active ? "Active" : "Suspended"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => toggleUserStatus(user.id, user.is_active)}
                        className={`text-xs px-3 py-1 rounded-lg transition ${
                          user.is_active
                            ? "bg-red-50 text-red-600 hover:bg-red-100"
                            : "bg-green-50 text-green-600 hover:bg-green-100"
                        }`}
                      >
                        {user.is_active ? "Suspend" : "Reactivate"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Projects Tab */}
      {activeTab === "projects" && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-gray-600 text-left border-b text-xs uppercase tracking-wide">
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project) => (
                  <tr key={project.id} className="border-b hover:bg-gray-50 transition">
                    <td className="px-4 py-3 text-gray-400">{project.id}</td>
                    <td className="px-4 py-3 text-gray-800">{project.title}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`text-xs font-semibold px-2 py-1 rounded capitalize ${
                          project.status === "open"
                            ? "text-green-700 bg-green-50"
                            : project.status === "disabled"
                            ? "text-red-700 bg-red-50"
                            : "text-gray-700 bg-gray-50"
                        }`}
                      >
                        {project.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {project.status !== "disabled" && (
                        <button
                          onClick={() => disableProject(project.id)}
                          className="text-xs px-3 py-1 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition"
                        >
                          Disable
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}