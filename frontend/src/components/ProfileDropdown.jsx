import { useState, useEffect, useRef, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

/**
 * ProfileDropdown
 *
 * Avatar circle in the navbar that opens a dropdown with:
 * - User name / email
 * - Profile link (role-appropriate)
 * - Logout button
 *
 * Replaces the plain text Logout button.
 */
export default function ProfileDropdown() {
  const { name, email, role, logout, profileComplete } = useContext(AuthContext);
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const navigate = useNavigate();

  // Close on outside click
  useEffect(() => {
    function handleOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  const profilePath = role === "student" ? "/profile" : "/organization/profile";
  const displayName = name || email || "?";
  const initials = displayName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="relative" ref={ref}>

      {/* Avatar button */}
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="relative flex items-center justify-center w-9 h-9 rounded-full
                   bg-primary text-white font-bold text-sm
                   hover:bg-primaryLight transition focus:outline-none focus:ring-2
                   focus:ring-primary focus:ring-offset-2"
        aria-label="Profile menu"
      >
        {initials}

        {/* Incomplete profile dot */}
        {!profileComplete && (
          <span className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-amber-400
                           rounded-full border-2 border-white" />
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg
                        border border-gray-100 z-50 overflow-hidden">

          {/* User info header */}
          <div className="px-4 py-3 border-b border-gray-100">
            <p className="text-sm font-semibold text-gray-800 truncate">
              {name || "User"}
            </p>
            <p className="text-xs text-gray-400 truncate">{email}</p>
            <span className="mt-1 inline-block text-xs px-2 py-0.5 rounded-full
                             bg-primaryBg text-primary font-medium capitalize">
              {role}
            </span>
          </div>

          {/* Menu items */}
          <ul className="py-1">
            {role !== "admin" && (
              <li>
                <button
                  onClick={() => { setOpen(false); navigate(profilePath); }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700
                             hover:bg-primaryBg transition flex items-center gap-2"
                >
                  <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24"
                       stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {profileComplete ? "My Profile" : (
                    <span className="flex items-center gap-1">
                      My Profile
                      <span className="text-xs bg-amber-100 text-amber-600
                                       px-1.5 py-0.5 rounded-full font-medium">
                        Set up
                      </span>
                    </span>
                  )}
                </button>
              </li>
            )}

            <li>
              <button
                onClick={() => { setOpen(false); logout(); }}
                className="w-full text-left px-4 py-2 text-sm text-red-500
                           hover:bg-red-50 transition flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24"
                     stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 
                       3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </li>
          </ul>

        </div>
      )}
    </div>
  );
}