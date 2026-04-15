import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../api/api";

/**
 * OrganizationProfilePage
 *
 * Handles view / edit / create states for organization profiles.
 *
 * API endpoints used:
 *   GET    /organization/profile
 *   POST   /organization/profile
 *   PUT    /organization/profile
 */
export default function OrganizationProfilePage() {
  const { name, email, setProfileComplete } = useContext(AuthContext);

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [mode, setMode] = useState("view"); // "view" | "edit" | "create"
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    organization_name: "",
    industry: "",
    website: "",
    description: "",
  });

  // ----------------------------
  // Fetch profile on mount
  // ----------------------------
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get("/organization/profile");
        setProfile(res.data);
        setForm({
          industry: res.data.industry || "",
          website: res.data.website || "",
          description: res.data.description || "",
        });
        setMode("view");
      } catch (err) {
        if (err.response?.status === 404) {
          setMode("create");
        } else {
          setError("Failed to load profile.");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const clearMessages = () => {
    setError(null);
    setSuccessMsg(null);
  };

  // ----------------------------
  // Create profile
  // ----------------------------
  const handleCreate = async (e) => {
    e.preventDefault();
    clearMessages();
    setSaving(true);
    try {
      const res = await api.post("/organization/profile", {
        organization_name: name,
        industry: form.industry || null,
        website: form.website || null,
        description: form.description || null,
      });
      setProfile(res.data);
      setMode("view");
      setProfileComplete(true);
      setSuccessMsg("Profile created successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create profile.");
    } finally {
      setSaving(false);
    }
  };

  // ----------------------------
  // Save edits
  // ----------------------------
  const handleSave = async (e) => {
    e.preventDefault();
    clearMessages();
    setSaving(true);
    try {
      const res = await api.put("/organization/profile", {
        industry: form.industry || null,
        website: form.website || null,
        description: form.description || null,
      });
      setProfile(res.data);
      setMode("view");
      setProfileComplete(true);
      setSuccessMsg("Profile updated successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  const handleEditClick = () => {
    clearMessages();
    setForm({
      industry: profile.industry || "",
      website: profile.website || "",
      description: profile.description || "",
    });
    setMode("edit");
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24 text-gray-400">
        Loading profile...
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">

      {/* Page header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Organization Profile</h1>
        {mode === "view" && (
          <button
            onClick={handleEditClick}
            className="bg-primary text-white px-4 py-2 rounded-lg
                       hover:bg-primaryLight transition text-sm font-medium">
            Edit Profile
          </button>
        )}
      </div>

      {/* Success banner */}
      {successMsg && (
        <div className="mb-4 px-4 py-3 rounded-lg bg-green-50 text-green-700
                        border border-green-200 text-sm">
          ✓ {successMsg}
        </div>
      )}

      {/* Error banner */}
      {error && (
        <div className="mb-4 px-4 py-3 rounded-lg bg-red-50 text-red-600
                        border border-red-200 text-sm">
          {error}
        </div>
      )}

      {/* ==============================
          VIEW MODE
      ============================== */}
      {mode === "view" && profile && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">

          {/* Header band */}
          <div className="bg-primaryBg px-8 py-6 flex items-center gap-5">
            <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center
                            text-white text-2xl font-bold flex-shrink-0">
              {(profile.organization_name || "O")[0].toUpperCase()}
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">
                {profile.organization_name}
              </h2>
              <p className="text-sm text-gray-500">{email}</p>
            </div>
          </div>

          {/* Details */}
          <div className="px-8 py-6 space-y-5">

            <div className="grid grid-cols-2 gap-4">

              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Industry</p>
                <p className="font-medium text-gray-700">
                  {profile.industry || <span className="text-gray-400 italic">Not specified</span>}
                </p>
              </div>

              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Website</p>
                {profile.website ? (
                  <a
                    href={profile.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline font-medium text-sm break-all"
                    >
                    {profile.website}
                  </a>
                ) : (
                  <p className="text-gray-400 italic text-sm">Not specified</p>
                )}
              </div>

            </div>

            {/* Description */}
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">About</p>
              {profile.description ? (
                <p className="text-sm text-gray-600 leading-relaxed">
                  {profile.description}
                </p>
              ) : (
                <p className="text-sm text-gray-400 italic">No description added yet</p>
              )}
            </div>

          </div>
    
        </div>
      
      )}

      {/* ==============================
          CREATE / EDIT FORM
      ============================== */}
      {(mode === "create" || mode === "edit") && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
          <div className="mb-6 p-4 bg-primaryBg rounded-xl border border-primaryPale
                          flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center
                            text-white font-bold text-sm flex-shrink-0">
              {(name || "O")[0].toUpperCase()}
            </div>
            <div>
              <p className="font-semibold text-gray-800">{name}</p>
              {/* <p className="text-xs text-gray-500">Organization name from registration</p> */}
            </div>
          </div>


          <h2 className="text-lg font-semibold text-gray-700 mb-6">
            {mode === "create" ? "Tell us more about your organization" : "Edit Profile"}
          </h2>

          <form
            onSubmit={mode === "create" ? handleCreate : handleSave}
            className="space-y-5">

            {/* Industry */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Industry
                <span className="text-gray-400 font-normal ml-1">(optional)</span>
              </label>
              <input
                type="text"
                name="industry"
                value={form.industry}
                onChange={handleChange}
                placeholder="e.g. Software, Healthcare, Finance"
                className="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            {/* Website */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Website
                <span className="text-gray-400 font-normal ml-1">(optional)</span>
              </label>
              <input
                type="url"
                name="website"
                value={form.website}
                onChange={handleChange}
                placeholder="https://yourcompany.com"
                className="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                About
                <span className="text-gray-400 font-normal ml-1">(optional)</span>
              </label>
              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                placeholder="Tell students about your organization, your mission, and the type of work you post..."
                rows={4}
                className="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              />
            </div>

            {/* Buttons */}
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={saving}
                className="bg-primary text-white px-6 py-2 rounded-lg text-sm font-medium
                           hover:bg-primaryLight transition disabled:opacity-50"
              >
                {saving
                  ? mode === "create" ? "Creating..." : "Saving..."
                  : mode === "create" ? "Create Profile" : "Save Changes"
                }
              </button>

              {mode === "edit" && (
                <button
                  type="button"
                  onClick={() => { setMode("view"); clearMessages(); }}
                  className="border border-gray-200 text-gray-600 px-6 py-2 rounded-lg
                             text-sm font-medium hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
              )}
            </div>

          </form>
        </div>
      )}
    </div>
  );
}