import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../api/api";

export default function CreateProject() {
  const { token } = useContext(AuthContext);
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [duration, setDuration] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  if (loading) return;
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await api.post("/projects", {
        title,
        description,
        required_skills: requiredSkills || null,
        duration: duration || null,
      });

      // Clear form fields
      setTitle("");
      setDescription("");
      setRequiredSkills("");
      setDuration("");

      // Redirect
      navigate("/projects");

    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to create project"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-md">
      <h2 className="text-2xl font-bold text-indigo-600 mb-6">
        Create New Project
      </h2>

      {error && (
        <div className="mb-4 text-red-600 bg-red-50 p-3 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* Title */}
        <div>
          <label className="block font-medium mb-2">Project Title *</label>
          <input
            type="text"
            className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        {/* Description */}
        <div>
          <label className="block font-medium mb-2">Description *</label>
          <textarea
            className="w-full border rounded-lg px-4 py-2 h-32 focus:ring-2 focus:ring-indigo-500"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>

        {/* Required Skills */}
        <div>
          <label className="block font-medium mb-2">
            Required Skills (comma separated)
          </label>
          <input
            type="text"
            placeholder="React, Python, SQL"
            className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
            value={requiredSkills}
            onChange={(e) => setRequiredSkills(e.target.value)}
          />
        </div>

        {/* Duration */}
        <div>
          <label className="block font-medium mb-2">
            Duration (e.g. 3 months, 6 weeks)
          </label>
          <input
            type="text"
            className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
        >
          {loading ? "Creating..." : "Create Project"}
        </button>

      </form>
    </div>
  );
}