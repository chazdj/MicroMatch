import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { getStudentAnalytics, getOrganizationAnalytics } from "../api/analytics";

// ── Simple SVG bar chart ──────────────────────────────────────────────────────
function BarChart({ bars }) {
  const max = Math.max(...bars.map((b) => b.value), 1);
  const chartH = 140;
  const topPad = 24;
  const barW = 56;
  const gap = 40;
  const totalW = bars.length * (barW + gap) - gap + 16;
  const svgH = chartH + topPad + 36;

  return (
    <div className="h-56 flex items-end">
    <svg
        viewBox={`0 0 ${totalW} ${svgH}`}
        className="w-full h-full"
        preserveAspectRatio="xMidYMax meet"
        aria-label="Analytics bar chart"
    >
      {bars.map((bar, i) => {
        const x = i * (barW + gap) + 8;
        const barH = Math.max((bar.value / max) * chartH, 4);
        const y = topPad + (chartH - barH);
        return (
          <g key={bar.label}>
            {/* Bar */}
            <rect
              x={x}
              y={y}
              width={barW}
              height={barH}
              rx={6}
              fill="#fe8997"
              opacity={0.85}
            />
            {/* Value label above bar */}
            <text
              x={x + barW / 2}
              y={y - 6}
              textAnchor="middle"
              fontSize="12"
              fontWeight="600"
              fill="#374151"
            >
              {bar.value}
            </text>
            {/* X-axis label below bar */}
            <text
              x={x + barW / 2}
              y={topPad + chartH + 18}
              textAnchor="middle"
              fontSize="10"
              fill="#9ca3af"
            >
              {bar.label}
            </text>
          </g>
        );
      })}
      {/* Baseline */}
      <line
        x1="4"
        y1={topPad + chartH}
        x2={totalW - 4}
        y2={topPad + chartH}
        stroke="#f3f4f6"
        strokeWidth="1.5"
      />
    </svg>
    </div>
  );
}

// ── Stat card ─────────────────────────────────────────────────────────────────
function StatCard({ icon, label, value, sub }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex items-start gap-4">
      <div className="text-3xl leading-none">{icon}</div>
      <div>
        <p className="text-2xl font-bold text-gray-800">
          {value ?? <span className="text-gray-300">—</span>}
        </p>
        <p className="text-sm font-medium text-gray-600 mt-0.5">{label}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

// ── Skeleton loader ───────────────────────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 animate-pulse">
      <div className="h-8 w-16 bg-gray-100 rounded mb-2" />
      <div className="h-4 w-28 bg-gray-100 rounded" />
    </div>
  );
}

// ── Student dashboard ─────────────────────────────────────────────────────────
function StudentDashboard({ data }) {
  const bars = [
    { label: "Submitted", value: data.applications_submitted },
    { label: "Accepted", value: data.accepted_applications },
    { label: "Completed", value: data.completed_projects },
  ];

  return (
    <>
      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon="📋"
          label="Applications Submitted"
          value={data.applications_submitted}
        />
        <StatCard
          icon="✅"
          label="Accepted"
          value={data.accepted_applications}
        />
        <StatCard
          icon="🏁"
          label="Completed Projects"
          value={data.completed_projects}
        />
        <StatCard
          icon="⭐"
          label="Avg. Feedback Rating"
          value={
            data.average_feedback_rating !== null
              ? `${data.average_feedback_rating} / 5`
              : null
          }
          sub={data.average_feedback_rating === null ? "No ratings yet" : undefined}
        />
      </div>

      {/* Bar chart */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">
          Application Overview
        </h3>
        <BarChart bars={bars} />
      </div>
    </>
  );
}

// ── Organization dashboard ────────────────────────────────────────────────────
function OrganizationDashboard({ data }) {
  const bars = [
    { label: "Total", value: data.total_projects_posted },
    { label: "Active", value: data.active_projects },
    { label: "Completed", value: data.completed_projects },
    { label: "Applicants", value: data.total_applicants },
  ];

  return (
    <>
      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon="📁"
          label="Projects Posted"
          value={data.total_projects_posted}
        />
        <StatCard
          icon="🟢"
          label="Active Projects"
          value={data.active_projects}
        />
        <StatCard
          icon="🏁"
          label="Completed Projects"
          value={data.completed_projects}
        />
        <StatCard
          icon="👥"
          label="Total Applicants"
          value={data.total_applicants}
          sub="unique students"
        />
      </div>

      {/* Bar chart */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">
          Project & Applicant Overview
        </h3>
        <BarChart bars={bars} />
      </div>
    </>
  );
}

// ── Main export ───────────────────────────────────────────────────────────────
export default function AnalyticsDashboard() {
  const { role } = useContext(AuthContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!role || role === "admin") {
      setLoading(false);
      return;
    }

    const fetch =
      role === "student" ? getStudentAnalytics : getOrganizationAnalytics;

    fetch()
      .then(setData)
      .catch((err) =>
        setError(err.response?.data?.detail || "Failed to load analytics.")
      )
      .finally(() => setLoading(false));
  }, [role]);

  // Admins don't have an analytics view
  if (role === "admin") return null;

  return (
    <div className="mt-10">
      {/* Section header */}
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-xl font-bold text-gray-700">📊 Your Analytics</h2>
        {!loading && !error && data && (
          <span className="text-xs text-gray-400">Live data</span>
        )}
      </div>

      {/* Loading skeletons */}
      {loading && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          {[...Array(4)].map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="rounded-xl border border-red-100 bg-red-50 p-5 text-sm text-red-500">
          {error}
        </div>
      )}

      {/* Data */}
      {!loading && !error && data && (
        <>
          {role === "student" && <StudentDashboard data={data} />}
          {role === "organization" && <OrganizationDashboard data={data} />}
        </>
      )}
    </div>
  );
}