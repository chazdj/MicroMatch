import { useState } from "react";
import api from "../api/api";

export default function FeedbackForm({ projectId, onSubmitted }) {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async () => {
    if (rating < 1 || rating > 5) {
      setError("Please select a rating between 1 and 5.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.post("/feedback", { project_id: projectId, rating, comment });
      setSuccess(true);
      if (onSubmitted) onSubmitted();
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to submit feedback.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
        <p className="text-green-700 font-medium">✓ Feedback submitted successfully!</p>
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 border rounded-lg bg-gray-50">
      <h3 className="text-lg font-semibold mb-3">Leave Feedback</h3>

      {error && (
        <p className="mb-3 text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded">
          {error}
        </p>
      )}

      <div className="mb-3">
        <label className="block text-sm font-medium mb-1">Rating (1–5)</label>
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map(n => (
            <button
              key={n}
              onClick={() => setRating(n)}
              className={`w-9 h-9 rounded-full border font-bold text-sm transition
                ${rating === n
                  ? "bg-primary text-white border-primary"
                  : "bg-white text-gray-700 border-gray-300 hover:border-primaryLight"
                }`}
            >
              {n}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-3">
        <label className="block text-sm font-medium mb-1">Comment (optional)</label>
        <textarea
          value={comment}
          onChange={e => setComment(e.target.value)}
          rows={3}
          className="w-full border rounded p-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Share your experience..."
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="px-4 py-2 bg-primary text-white rounded hover:bg-primaryLight disabled:opacity-50 text-sm font-medium"
      >
        {loading ? "Submitting..." : "Submit Feedback"}
      </button>
    </div>
  );
}