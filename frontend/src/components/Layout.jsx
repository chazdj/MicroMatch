import { Link } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

export default function Layout({ children }) {
  const { email, logout } = useContext(AuthContext);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-md px-8 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-indigo-600">
          MicroMatch
        </h1>

        <div className="space-x-6 flex items-center">
          <Link className="hover:text-indigo-600" to="/">
            Dashboard
          </Link>
          <Link className="hover:text-indigo-600" to="/projects">
            Projects
          </Link>
          <Link className="hover:text-indigo-600" to="/my-applications">
            My Applications
          </Link>
          <button
            onClick={logout}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
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