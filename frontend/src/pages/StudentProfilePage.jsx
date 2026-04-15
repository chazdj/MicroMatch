import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../api/api";

/**
 * StudentProfilePage
 *
 * Handles both the "view profile" and "edit profile" states in one page.
 * Also handles the "no profile yet" state with a create form.
 *
 * States:
 * - loading     → fetching profile from API
 * - no profile  → show create form
 * - view mode   → show profile card with Edit button
 * - edit mode   → show editable form with Save / Cancel
 */
export default function StudentProfilePage() {
  const { name, email, setProfileComplete } = useContext(AuthContext);

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [mode, setMode] = useState("view"); // "view" | "edit" | "create"
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    university: "",
    major: "",
    graduation_year: "",
    skills: "",
    bio: "",
  });

  // ----------------------------
  // Fetch profile on mount
  // ----------------------------
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get("/student/profile");
        setProfile(res.data);
        setForm({
          university: res.data.university || "",
          major: res.data.major || "",
          graduation_year: res.data.graduation_year || "",
          skills: res.data.skills || "",
          bio: res.data.bio || "",
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
    if (!form.university || !form.major || !form.graduation_year) {
      setError("University, major, and graduation year are required.");
      return;
    }
    setSaving(true);
    try {
      const res = await api.post("/student/profile", {
        ...form,
        graduation_year: parseInt(form.graduation_year),
        skills: form.skills || null,
        bio: form.bio || null,
      });
      setProfile(res.data);
      setMode("view");
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
      const res = await api.put("/student/profile", {
        ...form,
        graduation_year: parseInt(form.graduation_year),
        skills: form.skills || null,
        bio: form.bio || null,
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
      university: profile.university || "",
      major: profile.major || "",
      graduation_year: profile.graduation_year || "",
      skills: profile.skills || "",
      bio: profile.bio || "",
    });
    setMode("edit");
  };

  // ----------------------------
  // Parse skills into chips
  // ----------------------------
  const parseSkills = (raw) => {
    if (!raw) return [];
    return raw.split(",").map((s) => s.trim()).filter(Boolean);
  };

  // ----------------------------
  // Loading
  // ----------------------------
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
        <h1 className="text-2xl font-bold text-gray-800">My Profile</h1>
        {mode === "view" && (
          <button
            onClick={handleEditClick}
            className="bg-primary text-white px-4 py-2 rounded-lg
                       hover:bg-primaryLight transition text-sm font-medium"
          >
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

          {/* Profile header band */}
          <div className="bg-primaryBg px-8 py-6 flex items-center gap-5">
            <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center
                            text-white text-2xl font-bold flex-shrink-0">
              {(name || email || "?")[0].toUpperCase()}
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">{name || email}</h2>
              <p className="text-sm text-gray-500">{email}</p>
            </div>
          </div>

          {/* Profile details */}
          <div className="px-8 py-6 space-y-5">

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">University</p>
                <p className="font-medium text-gray-700">{profile.university}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Major</p>
                <p className="font-medium text-gray-700">{profile.major}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Graduation Year</p>
                <p className="font-medium text-gray-700">{profile.graduation_year}</p>
              </div>
            </div>

            {/* Skills chips */}
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">Skills</p>
              {parseSkills(profile.skills).length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {parseSkills(profile.skills).map((skill) => (
                    <span
                      key={skill}
                      className="px-3 py-1 bg-primaryBg text-primary text-xs
                                 font-medium rounded-full border border-primaryPale"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400 italic">No skills added yet</p>
              )}
            </div>

            {/* Bio */}
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">Bio</p>
              {profile.bio 
              ? <p className="text-sm text-gray-600 leading-relaxed">{profile.bio}</p>
              : <p className="text-sm text-gray-400 italic">No bio added yet</p>
              }
            </div>

          </div>
        </div>
      )}

      {/* ==============================
          CREATE / EDIT FORM
      ============================== */}
      {(mode === "create" || mode === "edit") && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">

          <h2 className="text-lg font-semibold text-gray-700 mb-6">
            {mode === "create" ? "Complete Your Profile" : "Edit Profile"}
          </h2>

          <form
            onSubmit={mode === "create" ? handleCreate : handleSave}
            className="space-y-5"
          >

            {/* University */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                University <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                name="university"
                value={form.university}
                onChange={handleChange}
                placeholder="e.g. University of Florida"
                className="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-primary"
                required
              />
            </div>

            {/* Major */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Major <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                name="major"
                value={form.major}
                onChange={handleChange}
                placeholder="e.g. Computer Science"
                className="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-primary"
                required
              />
            </div>

            {/* Graduation Year */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Graduation Year <span className="text-red-400">*</span>
              </label>
              <input
                type="number"
                name="graduation_year"
                value={form.graduation_year}
                onChange={handleChange}
                placeholder="e.g. 2026"
                min="2018"
                max="2035"
                className="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-primary"
                required
              />
            </div>

            {/* Skills */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Skills
                <span className="text-gray-400 font-normal ml-1">(comma separated)</span>
              </label>
              <input
                type="text"
                name="skills"
                value={form.skills}
                onChange={handleChange}
                placeholder="Python, FastAPI, React, SQL"
                className="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-primary"
              />
              {/* Live skill chip preview */}
              {parseSkills(form.skills).length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {parseSkills(form.skills).map((s) => (
                    <span
                      key={s}
                      className="px-2 py-0.5 bg-primaryBg text-primary text-xs
                                 rounded-full border border-primaryPale"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Bio */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bio
                <span className="text-gray-400 font-normal ml-1">(optional)</span>
              </label>
              <textarea
                name="bio"
                value={form.bio}
                onChange={handleChange}
                placeholder="Tell organizations about yourself, your interests, and what you're looking for..."
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