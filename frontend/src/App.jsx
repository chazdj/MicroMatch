import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import ProjectsPage from "./pages/ProjectsPage";
import PrivateRoute from "./components/PrivateRoute";
import MyApplications from "./pages/MyApplications";
import OrganizationApplicationsDashboard from "./pages/OrganizationApplicationDashboard";
import Layout from "./components/Layout";

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes */}
          <Route path="/" element={<PrivateRoute><Layout><Home /></Layout></PrivateRoute>} />
          <Route path="/projects" element={<PrivateRoute><Layout><ProjectsPage /></Layout></PrivateRoute>} />
          <Route path="/my-applications" element={<PrivateRoute><Layout><MyApplications /></Layout></PrivateRoute>} />
          <Route path="/organization/applications" element={<PrivateRoute allowedRoles={["organization"]}><Layout><OrganizationApplicationsDashboard /></Layout></PrivateRoute>} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;