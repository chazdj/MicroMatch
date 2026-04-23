import { Link } from "react-router-dom";
import { useContext, useState, useEffect, useCallback } from "react";
import { AuthContext } from "../context/AuthContext";
import NotificationBell from "./NotificationBell";
import ProfileDropdown from "./ProfileDropdown";
import ProfileSetupBanner from "./ProfileSetupBanner";
import api from "../api/api";

export default function Layout({ children }) {
  const { role, loading } = useContext(AuthContext);

  const [notifications, setNotifications] = useState([]);
  const [notifLoading, setNotifLoading] = useState(true);
  const [notifError, setNotifError] = useState(null);

  // ----------------------------
  // Fetch notifications
  // ----------------------------
  const fetchNotifications = useCallback(async () => {
    try {
      const res = await api.get("/notifications");
      setNotifications(res.data);
      setNotifError(null);
    } catch (err) {
      setNotifError("Failed to load notifications");
    } finally {
      setNotifLoading(false);
    }
  }, []);

  // Fetch on mount + poll every 30 seconds
  useEffect(() => {
    if (loading) return;
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [loading, fetchNotifications]);

  // ----------------------------
  // Mark a notification as read
  // Updates local state immediately (optimistic), then persists to API
  // ----------------------------
  const handleMarkRead = useCallback(async (id) => {
    // Optimistic update — update UI instantly before API responds
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );

    try {
      await api.put(`/notifications/${id}/read`);
    } catch (err) {
      // If API call fails, revert the optimistic update
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: false } : n))
      );
    }
  }, []);

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
            <>
              <Link className="hover:text-primary transition" to="/my-applications">
                My Applications
              </Link>
              <Link className="hover:text-primary transition" to="/messages">
                Messages
              </Link>
            </>
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
              <Link className="hover:text-primary transition" to="/messages">
                Messages
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

          {/* Notification Bell */}
          <NotificationBell
            notifications={notifications}
            onMarkRead={handleMarkRead}
          />

          {/* Profile Dropdown */}
          <ProfileDropdown />

        </div>
      </nav>

      {/* Profile Setup Banner */}
      <ProfileSetupBanner />

      {/* Page Content */}
      <main className="max-w-6xl mx-auto py-10 px-6">
        {/* Pass notification state into NotificationsPage */}
        {children?.type?.name === "NotificationsPage"
          ? <children.type
              {...children.props}
              notifications={notifications}
              loading={notifLoading}
              error={notifError}
              onMarkRead={handleMarkRead}
            />
          : children
        }
      </main>

    </div>
  );
}