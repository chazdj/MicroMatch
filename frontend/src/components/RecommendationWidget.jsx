import { useState, useEffect } from "react";
import api from "../api/api";

/**
 * RecommendationWidget
 *
 * Displays ranked project recommendations on the student dashboard.
 * Fetches from GET /recommendations and renders scored project cards
 * with match score badges and quick-apply CTAs.
 *
 * Handles:
 * - Loading state
 * - No profile yet (404) → prompt to create profile
 * - Empty recommendations → friendly empty state
 * - Apply flow with per-card feedback
 * - Error state
 */
export default function RecommendationWidget() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [noProfile, setNoProfile] = useState(false);
  const [error, setError] = useState(null);

  // Per-card apply state
  const [applying, setApplying] = useState({});
  const [applyMessages, setApplyMessages] = useState({});

  // ── Fetch recommendations ───────────────────────────────────────────────
  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.get("/recommendations");
        setRecommendations(res.data);
      } catch (err) {
        if (err.response?.status === 404) {
          // Student has no profile yet — not a real error
          setNoProfile(true);
        } else {
          setError(err.response?.data?.detail || "Failed to load recommendations.");
        }
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  // ── Apply to a project ──────────────────────────────────────────────────
  const handleApply = async (projectId) => {
    setApplying((prev) => ({ ...prev, [projectId]: true }));
    setApplyMessages((prev) => ({ ...prev, [projectId]: null }));

    try {
      await api.post("/applications", { project_id: projectId });
      setApplyMessages((prev) => ({
        ...prev,
        [projectId]: { type: "success", text: "Application submitted!" },
      }));
    } catch (err) {
      setApplyMessages((prev) => ({
        ...prev,
        [projectId]: {
          type: "error",
          text: err.response?.data?.detail || "Failed to apply.",
        },
      }));
    } finally {
      setApplying((prev) => ({ ...prev, [projectId]: false }));
    }
  };

  // ── Score badge color ───────────────────────────────────────────────────
  // Green ≥ 70 | Yellow ≥ 40 | Red < 40
  const badgeClass = (score) => {
    if (score >= 70) return "bg-green-100 text-green-700 border-green-200";
    if (score >= 40) return "bg-yellow-100 text-yellow-700 border-yellow-200";
    return "bg-red-100 text-red-600 border-red-200";
  };

  // ── Render states ───────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="mt-10">
        <h2 className="text-xl font-bold text-gray-700 mb-4">⭐ Best Matches For You</h2>
        <p className="text-gray-400 text-sm">Finding your best matches...</p>
      </div>
    );
  }

  if (noProfile) {
    return (
      <div className="mt-10">
        <h2 className="text-xl font-bold text-gray-700 mb-4">⭐ Best Matches For You</h2>
        <div className="rounded-xl border border-primaryPale bg-primaryBg p-6 text-center">
          <p className="text-gray-600 mb-2 font-medium">
            Complete your student profile to unlock personalised recommendations.
          </p>
          <p className="text-gray-400 text-sm">
            Add your skills, major, and bio so we can match you with the best projects.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-10">
        <h2 className="text-xl font-bold text-gray-700 mb-4">⭐ Best Matches For You</h2>
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="mt-10">
        <h2 className="text-xl font-bold text-gray-700 mb-4">⭐ Best Matches For You</h2>
        <div className="rounded-xl border border-gray-100 bg-white p-6 text-center">
          <p className="text-4xl mb-3">🔍</p>
          <p className="text-gray-500">No open projects available right now.</p>
          <p className="text-gray-400 text-sm mt-1">Check back soon for new opportunities.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-10">

      {/* Section header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-700">⭐ Best Matches For You</h2>
        <span className="text-xs text-gray-400">{recommendations.length} project{recommendations.length !== 1 ? "s" : ""} ranked</span>
      </div>

      {/* Project cards grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {recommendations.map((rec) => (
          <div
            key={rec.project_id}
            className="bg-white rounded-xl border border-gray-100 shadow-sm
                       hover:shadow-md hover:border-primaryPale transition-all
                       flex flex-col justify-between p-5"
          >
            {/* Card top */}
            <div>

              {/* Rank + score badge row */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-gray-400 font-medium">
                  #{rec.rank}
                </span>
                <span className={`text-xs font-bold px-2.5 py-1 rounded-full border ${badgeClass(rec.match_score)}`}>
                  {rec.match_score.toFixed(0)}% match
                </span>
              </div>

              {/* Title */}
              <h3 className="font-semibold text-gray-800 text-sm leading-snug mb-2">
                {rec.title}
              </h3>

              {/* Score breakdown bar */}
              <div className="mb-3">
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div
                    className="bg-primary h-1.5 rounded-full transition-all"
                    style={{ width: `${Math.min(rec.match_score, 100)}%` }}
                  />
                </div>
              </div>

              {/* Score breakdown detail */}
              <div className="space-y-1 mb-3">
                {[
                  { label: "Skills", value: rec.skill_score },
                  { label: "Experience", value: rec.experience_score },
                  { label: "Interests", value: rec.interest_score },
                ].map(({ label, value }) => (
                  <div key={label} className="flex justify-between items-center text-xs text-gray-500">
                    <span>{label}</span>
                    <span className="font-medium">{value.toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Card bottom — apply CTA */}
            <div className="mt-auto pt-3 border-t border-gray-50">
              {applyMessages[rec.project_id] ? (
                <p className={`text-xs font-medium text-center py-1 ${
                  applyMessages[rec.project_id].type === "success"
                    ? "text-green-600"
                    : "text-red-500"
                }`}>
                  {applyMessages[rec.project_id].text}
                </p>
              ) : (
                <button
                  onClick={() => handleApply(rec.project_id)}
                  disabled={applying[rec.project_id]}
                  className="w-full py-2 rounded-lg text-sm font-semibold transition
                             bg-primary text-white hover:bg-primaryLight
                             disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {applying[rec.project_id] ? "Applying..." : "Quick Apply"}
                </button>
              )}
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}