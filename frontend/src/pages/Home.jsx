import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import RecommendationWidget from "../components/RecommendationWidget";

/**
 * Home page / dashboard shown after login.
 *
 * - All users see a welcome message.
 * - Students additionally see the RecommendationWidget with ranked
 *   project matches powered by the SA-1 matching algorithm.
 * - Organization and admin users see a role-appropriate message.
 */
export default function Home() {
  const { name, email, role } = useContext(AuthContext);

  return (
    <div>

      {/* Welcome header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Welcome back, {name || email} 
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          {role === "student" && "Here are the projects best matched to your profile."}
          {role === "organization" && "Manage your projects and review applications from your dashboard."}
          {role === "admin" && "Monitor system activity and manage platform content."}
        </p>
      </div>

      {/* Student — Recommendations widget */}
      {role === "student" && (
        <RecommendationWidget />
      )}

      {/* Organization — quick links */}
      {role === "organization" && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
          {[
            { label: "View Applications", href: "/organization/applications" },
            { label: "Create Project", href: "/organization/create-project" },
            { label: "Deliverables", href: "/organization/deliverables" },
          ].map(({ label, href }) => (
            <a
              key={href}
              href={href}
              className="block p-5 bg-white rounded-xl border border-gray-100
                         shadow-sm hover:shadow-md hover:border-primaryPale
                         transition text-center font-medium text-gray-700 text-sm"
            >
              {label}
            </a>
          ))}
        </div>
      )}

      {/* Admin — quick links */}
      {role === "admin" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
          {[
            { label: "System Logs", href: "/admin/logs" },
            { label: "Moderation", href: "/admin/moderation" },
          ].map(({ label, href }) => (
            <a
              key={href}
              href={href}
              className="block p-5 bg-white rounded-xl border border-gray-100
                         shadow-sm hover:shadow-md hover:border-primaryPale
                         transition text-center font-medium text-gray-700 text-sm"
            >
              {label}
            </a>
          ))}
        </div>
      )}

    </div>
  );
}