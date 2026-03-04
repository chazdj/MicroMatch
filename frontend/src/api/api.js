import axios from "axios";

// Create axios instance
const api = axios.create({
  baseURL: "http://localhost:8000",
});

// ----------------------------
// Request Interceptor
// Automatically attach JWT
// ----------------------------
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ----------------------------
// Response Interceptor
// Auto logout on 401
// ----------------------------
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("email");

      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

export default api;