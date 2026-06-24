import api from "./api";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

/**
 * Fetch all messages for a project, ordered oldest → newest.
 */
export const getMessages = (projectId) =>
  api.get(`/projects/${projectId}/messages`).then((res) => res.data);

/**
 * Send a message in a project.
 */
export const sendMessage = (projectId, content) =>
  api.post(`/projects/${projectId}/messages`, { content }).then((res) => res.data);