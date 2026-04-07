import { Link } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

export default function Layout({ children }) {
  const { email, role, logout, loading } = useContext(AuthContext);

  if (loading) return null;

  return (
    <div className="min-h-screen bg-gray-50">

      {/* Navbar */}
      <nav className="bg-white shadow-md px-8 py-4 flex justify-between items-center border-b border-primaryPale">

        <h1 className="text-xl font-bold text-primary">
          MicroMatch
        </h1>

        <div className="space-x-6 flex items-center">

          {/* Common Links */}
          <Link className="hover:text-primary transition" to="/">
            Dashboard
          </Link>

          <Link className="hover:text-primary transition" to="/projects">
            Projects
          </Link>

          {/* Student Only Links */}
          {role === "student" && (
            <Link className="hover:text-primary transition" to="/my-applications">
              My Applications
            </Link>
          )}

          {/* Organization Only Links */}
          {role === "organization" && (
            <>
              <Link className="hover:text-primary transition" to="/organization/applications">
                Applications Dashboard
              </Link>
              <Link className="hover:text-primary transition" to="/organization/create-project">
                Create Project
              </Link>
              <Link className="hover:text-primary transition" to="/organization/deliverables">
                  Deliverables
              </Link>
            </>
          )}

          {/* Admin Only Links */}
          {role === "admin" && (
            <>
              <Link className="hover:text-primary transition" to="/admin/logs">
                System Logs
              </Link>
              <Link className="hover:text-primary transition" to="/admin/moderation">
                Moderation
              </Link>
            </>
          )}


          <button
            onClick={logout}
            className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primaryLight transition"
          >
            Logout
          </button>

        </div>
      </nav>

      {/* Page Content */}
      <main className="max-w-6xl mx-auto py-10 px-6">
        {children}
      </main>

    </div>
  );
}