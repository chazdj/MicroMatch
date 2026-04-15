import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

/**
 * ProfileSetupBanner
 *
 * Shown at the top of every page when the user hasn't set up their profile yet.
 * Tapping "Set up now" navigates to the correct profile page for their role.
 */
export default function ProfileSetupBanner() {
  const { role, profileComplete } = useContext(AuthContext);
  const navigate = useNavigate();

  if (profileComplete) return null;

  const profilePath = role === "student" ? "/profile" : "/organization/profile";

  return (
    <div className="bg-amber-50 border-b border-amber-200 px-8 py-3
                    flex items-center justify-between gap-4">
      <div className="flex items-center gap-2 text-amber-800 text-sm">
        <span className="text-lg">👋</span>
        <span>
          Welcome to MicroMatch! Complete your profile so you can get the most out of the platform.
        </span>
      </div>
      <button
        onClick={() => navigate(profilePath)}
        className="flex-shrink-0 bg-amber-500 hover:bg-amber-600 text-white
                   text-xs font-semibold px-4 py-1.5 rounded-lg transition"
      >
        Set up now →
      </button>
    </div>
  );
}