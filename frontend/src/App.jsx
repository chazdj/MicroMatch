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
import CreateProject from "./pages/CreateProject";
import OrgDeliverablesDashboard from "./pages/OrgDeliverablesDashboard";

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
          <Route path="/my-applications" element={<PrivateRoute allowedRoles={["student"]}><Layout><MyApplications /></Layout></PrivateRoute>} />
          <Route path="/organization/applications" element={<PrivateRoute allowedRoles={["organization"]}><Layout><OrganizationApplicationsDashboard /></Layout></PrivateRoute>} />
          <Route path="/organization/create-project" element={<PrivateRoute allowedRoles={["organization"]}><Layout><CreateProject /></Layout></PrivateRoute>} />
          <Route path="/organization/deliverables" element={<PrivateRoute allowedRoles={["organization"]}><Layout><OrgDeliverablesDashboard /></Layout></PrivateRoute>} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;