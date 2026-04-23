import { useState, useEffect, useRef, useContext, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../api/api";
import { getMessages, sendMessage } from "../api/messages";

const POLL_INTERVAL_MS = 5000;

// ── Fetch projects the current user can message in ─────────────
async function fetchParticipantProjects(role) {
  if (role === "organization") {
    const res = await api.get("/projects/me");
    // Only projects that have at least one accepted student
    return res.data;
  } else {
    // Student: get accepted applications and extract projects
    const res = await api.get("/applications/me");
    return res.data
      .filter((a) => a.status === "accepted" && a.project)
      .map((a) => a.project);
  }
}

// ── Chat panel ─────────────────────────────────────────────────
function ChatPanel({ projectId, email }) {
  const [messages, setMessages] = useState([]);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);
  const pollRef = useRef(null);

  const fetchMessages = useCallback (async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const data = await getMessages(projectId);
      setMessages(data);
      setError(null);
    } catch (err) {
      setError("Failed to load messages.");
    } finally {
      if (showLoading) setLoading(false);
    }
}, [projectId]);

  useEffect(() => {
    setMessages([]);
    setContent("");
    setError(null);
    fetchMessages(true);
    pollRef.current = setInterval(() => fetchMessages(false), POLL_INTERVAL_MS);
    return () => clearInterval(pollRef.current);
  }, [projectId, fetchMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed || sending) return;
    setSending(true);
    try {
      const newMsg = await sendMessage(projectId, trimmed);
      setMessages((prev) => [...prev, newMsg]);
      setContent("");
    } catch {
      setError("Failed to send. Please try again.");
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  const isMine = (msg) => msg.sender?.email === email;

  const formatTime = (ts) =>
    new Date(ts).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        Loading conversation…
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {/* Error banner */}
      {error && (
        <div className="mx-4 mt-3 px-4 py-2 rounded-lg bg-red-50 border border-red-200 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* Thread */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
            <p className="text-4xl mb-3">💬</p>
            <p className="text-sm">No messages yet.</p>
            <p className="text-xs mt-1">Send the first message below.</p>
          </div>
        ) : (
          messages.map((msg) => {
            const mine = isMine(msg);
            return (
              <div
                key={msg.id}
                className={`flex flex-col ${mine ? "items-end" : "items-start"}`}
              >
                <span className="text-xs text-gray-400 mb-1 px-1">
                  {mine
                    ? "You"
                    : `${msg.sender?.email} · ${msg.sender?.role ?? ""}`}
                </span>
                <div
                  className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm ${
                    mine
                      ? "bg-primary text-white rounded-br-sm"
                      : "bg-white border border-gray-200 text-gray-800 rounded-bl-sm"
                  }`}
                >
                  {msg.content}
                </div>
                <span className="text-xs text-gray-300 mt-1 px-1">
                  {formatTime(msg.created_at)}
                </span>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>

      {/* Send box */}
      <form
        onSubmit={handleSend}
        className="flex items-end gap-2 border-t border-gray-100 px-4 py-3"
      >
        <textarea
          rows={2}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message… (Enter to send)"
          className="flex-1 resize-none rounded-xl border border-gray-200 px-4 py-2.5 text-sm
                     focus:outline-none focus:ring-2 focus:ring-primaryPale focus:border-primary
                     placeholder-gray-300 transition"
        />
        <button
          type="submit"
          disabled={!content.trim() || sending}
          className="px-5 py-2.5 rounded-xl bg-primary text-white text-sm font-medium
                     hover:opacity-90 transition disabled:opacity-40 disabled:cursor-not-allowed
                     flex-shrink-0 h-fit"
        >
          {sending ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}

// ── Main hub page ───────────────────────────────────────────────
export default function MessagesHubPage() {
  const { role, email } = useContext(AuthContext);
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [searchParams, setSearchParams] = useSearchParams();

  // Support deep-linking: /messages?project=42
  useEffect(() => {
    const fromUrl = parseInt(searchParams.get("project"));
    if (fromUrl) setSelectedId(fromUrl);
  }, [searchParams]);

  useEffect(() => {
    fetchParticipantProjects(role)
      .then((list) => {
        setProjects(list);
        // Auto-select first project if none set via URL param
        if (!selectedId && list.length > 0) {
          setSelectedId(list[0].id);
        }
      })
      .catch(() => setProjects([]))
      .finally(() => setLoadingProjects(false));
  }, [role, selectedId]);

  const handleSelect = (id) => {
    setSelectedId(id);
    setSearchParams({ project: id });
  };

  const selectedProject = projects.find((p) => p.id === selectedId);

  return (
    <div className="flex h-[calc(100vh-140px)] bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">

      {/* ── Left sidebar ── */}
      <aside className="w-64 flex-shrink-0 border-r border-gray-100 flex flex-col">
        <div className="px-4 py-4 border-b border-gray-100">
          <h2 className="text-base font-bold text-gray-800">Messages</h2>
          <p className="text-xs text-gray-400 mt-0.5">Your active projects</p>
        </div>

        <div className="flex-1 overflow-y-auto">
          {loadingProjects ? (
            <p className="text-xs text-gray-400 text-center mt-8">Loading…</p>
          ) : projects.length === 0 ? (
            <div className="text-center mt-10 px-4">
              <p className="text-3xl mb-2">💬</p>
              <p className="text-xs text-gray-400">
                No active projects yet.
              </p>
            </div>
          ) : (
            <ul className="py-2">
              {projects.map((p) => (
                <li key={p.id}>
                  <button
                    onClick={() => handleSelect(p.id)}
                    className={`w-full text-left px-4 py-3 text-sm transition hover:bg-primaryBg ${
                      selectedId === p.id
                        ? "bg-primaryBg border-r-2 border-primary font-medium text-primary"
                        : "text-gray-700"
                    }`}
                  >
                    <span className="block truncate">{p.title}</span>
                    <span className="block text-xs text-gray-400 mt-0.5 truncate">
                      #{p.id} · {p.status}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      {/* ── Right: chat area ── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Chat header */}
        {selectedProject ? (
          <div className="px-6 py-4 border-b border-gray-100 flex-shrink-0">
            <h3 className="font-semibold text-gray-800">{selectedProject.title}</h3>
            <p className="text-xs text-gray-400 mt-0.5">Project #{selectedProject.id}</p>
          </div>
        ) : (
          <div className="px-6 py-4 border-b border-gray-100 flex-shrink-0">
            <h3 className="font-semibold text-gray-400">Select a project to start messaging</h3>
          </div>
        )}

        {/* Chat panel or empty prompt */}
        {selectedId ? (
          <ChatPanel key={selectedId} projectId={selectedId} email={email} />
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-300 text-sm">
            ← Select a conversation
          </div>
        )}
      </div>
    </div>
  );
}