import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

/**
 * NotificationBell
 *
 * Renders the navbar bell icon with unread badge, dropdown preview,
 * and click-to-read interaction.
 *
 * Props:
 * - notifications: array of notification objects from parent
 * - onMarkRead: function(id) — called when a notification is clicked
 */
export default function NotificationBell({ notifications, onMarkRead }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const navigate = useNavigate();

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  // ----------------------------
  // Close dropdown on outside click
  // ----------------------------
  useEffect(() => {
    function handleClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // ----------------------------
  // Click a notification item:
  // mark as read then navigate
  // ----------------------------
  const handleNotificationClick = async (notification) => {
    if (!notification.is_read) {
      await onMarkRead(notification.id);
    }
    setOpen(false);
    navigate("/notifications");
  };

  // Show 5 most recent in dropdown preview
  const preview = notifications.slice(0, 5);

  return (
    <div className="relative" ref={ref}>

      {/* Bell button */}
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="relative p-2 rounded-full hover:bg-primaryBg transition focus:outline-none"
        aria-label="Notifications"
      >
        {/* Bell icon (inline SVG — no extra dependency) */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6 text-gray-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 
               6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 
               8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 
               0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>

        {/* Unread badge */}
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center
                           px-1.5 py-0.5 text-xs font-bold leading-none text-white
                           bg-primary rounded-full min-w-[18px]">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg
                        border border-gray-100 z-50 overflow-hidden">

          {/* Header */}
          <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100">
            <span className="font-semibold text-gray-700">Notifications</span>
            {unreadCount > 0 && (
              <span className="text-xs text-primary font-medium">
                {unreadCount} unread
              </span>
            )}
          </div>

          {/* Notification list */}
          {preview.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-6">
              No notifications yet
            </p>
          ) : (
            <ul className="max-h-72 overflow-y-auto divide-y divide-gray-50">
              {preview.map((n) => (
                <li
                  key={n.id}
                  onClick={() => handleNotificationClick(n)}
                  className={`px-4 py-3 cursor-pointer hover:bg-primaryBg transition text-sm
                    ${!n.is_read ? "bg-primaryBg font-medium" : "bg-white text-gray-500"}`}
                >
                  <p className="leading-snug">{n.message}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(n.created_at).toLocaleString()}
                  </p>
                </li>
              ))}
            </ul>
          )}

          {/* Footer — view all link */}
          <div
            onClick={() => { setOpen(false); navigate("/notifications"); }}
            className="text-center text-xs text-primary font-medium py-3
                       border-t border-gray-100 cursor-pointer hover:bg-primaryBg transition"
          >
            View all notifications →
          </div>

        </div>
      )}
    </div>
  );
}