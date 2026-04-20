/**
 * NotificationsPage
 *
 * Full notifications list page at /notifications.
 * Receives data and handlers from Layout via props — no duplicate fetch.
 *
 * Props:
 * - notifications: array
 * - loading: boolean
 * - error: string | null
 * - onMarkRead: function(id)
 */
export default function NotificationsPage({ notifications, loading, error, onMarkRead }) {

  const handleClick = async (notification) => {
    if (!notification.is_read) {
      await onMarkRead(notification.id);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-20 text-gray-400">
        Loading notifications...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20 text-red-500">
        {error}
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Notifications</h1>
        <span className="text-sm text-gray-400">
          {notifications.filter((n) => !n.is_read).length} unread
        </span>
      </div>

      {/* Empty state */}
      {notifications.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-4xl mb-4">🔔</p>
          <p>You have no notifications yet.</p>
        </div>
      ) : (
        <ul className="space-y-2">
          {notifications.map((n) => (
            <li
              key={n.id}
              onClick={() => handleClick(n)}
              className={`p-4 rounded-xl border cursor-pointer transition
                ${!n.is_read
                  ? "bg-primaryBg border-primaryPale font-medium hover:bg-pink-100"
                  : "bg-white border-gray-100 text-gray-500 hover:bg-gray-50"
                }`}
            >
              <div className="flex justify-between items-start gap-4">

                {/* Message */}
                <div className="flex items-start gap-3">
                  {/* Unread dot */}
                  {!n.is_read && (
                    <span className="mt-1.5 flex-shrink-0 w-2 h-2 rounded-full bg-primary" />
                  )}
                  <p className="text-sm leading-snug">{n.message}</p>
                </div>

                {/* Timestamp */}
                <p className="text-xs text-gray-400 flex-shrink-0 whitespace-nowrap">
                  {new Date(n.created_at).toLocaleString()}
                </p>

              </div>

              {/* Read indicator */}
              {n.is_read && (
                <p className="text-xs text-gray-300 mt-1 ml-0">✓ Read</p>
              )}
            </li>
          ))}
        </ul>
      )}

    </div>
  );
}