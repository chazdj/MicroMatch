import { useState, useEffect } from "react";
import api from "../api/api";

export default function AdminLogsDashboard() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [methodFilter, setMethodFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await api.get("/admin/logs");
      setLogs(res.data);
    } catch (err) {
      console.error("Failed to fetch logs", err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = logs.filter((log) => {
    const matchesSearch =
      !search || log.endpoint.toLowerCase().includes(search.toLowerCase());
    const matchesMethod =
      methodFilter === "ALL" || log.method === methodFilter;
    const matchesStatus =
      statusFilter === "ALL" ||
      (statusFilter === "2xx" && log.status_code >= 200 && log.status_code < 300) ||
      (statusFilter === "4xx" && log.status_code >= 400 && log.status_code < 500) ||
      (statusFilter === "5xx" && log.status_code >= 500);
    return matchesSearch && matchesMethod && matchesStatus;
  });

  const statusBadge = (code) => {
    if (code >= 200 && code < 300) return "text-green-700 bg-green-50";
    if (code >= 400 && code < 500) return "text-red-700 bg-red-50";
    if (code >= 500) return "text-orange-700 bg-orange-50";
    return "text-gray-700 bg-gray-50";
  };

  const methodBadge = (method) => {
    const map = {
      GET: "text-blue-700 bg-blue-50",
      POST: "text-green-700 bg-green-50",
      PUT: "text-yellow-700 bg-yellow-50",
      PATCH: "text-purple-700 bg-purple-50",
      DELETE: "text-red-700 bg-red-50",
    };
    return map[method] || "text-gray-700 bg-gray-50";
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">System Logs</h1>
        <p className="text-gray-500 text-sm mt-1">
          {filtered.length} {filtered.length === 1 ? "entry" : "entries"}
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search endpoint..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm w-60 focus:outline-none focus:ring-2 focus:ring-primary"
        />

        <select
          value={methodFilter}
          onChange={(e) => setMethodFilter(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="ALL">All Methods</option>
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="PATCH">PATCH</option>
          <option value="DELETE">DELETE</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="ALL">All Statuses</option>
          <option value="2xx">2xx Success</option>
          <option value="4xx">4xx Client Error</option>
          <option value="5xx">5xx Server Error</option>
        </select>

        <button
          onClick={fetchLogs}
          className="border rounded-lg px-4 py-2 text-sm hover:bg-gray-50 transition"
        >
          Refresh
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        {loading ? (
          <p className="text-center text-gray-400 py-10">Loading logs...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-gray-600 text-left border-b text-xs uppercase tracking-wide">
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">User ID</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Method</th>
                  <th className="px-4 py-3">Endpoint</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center text-gray-400 py-10">
                      No logs found.
                    </td>
                  </tr>
                ) : (
                  filtered.map((log) => (
                    <tr key={log.id} className="border-b hover:bg-gray-50 transition">
                      <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-gray-700">
                        {log.user_id ?? (
                          <span className="text-gray-400 italic">anon</span>
                        )}
                      </td>
                      <td className="px-4 py-3 capitalize text-gray-600">
                        {log.role ?? <span className="text-gray-400 italic">—</span>}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`font-mono text-xs font-semibold px-2 py-1 rounded ${methodBadge(log.method)}`}
                        >
                          {log.method}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono text-gray-700">
                        {log.endpoint}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`text-xs font-semibold px-2 py-1 rounded ${statusBadge(log.status_code)}`}
                        >
                          {log.status_code}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}