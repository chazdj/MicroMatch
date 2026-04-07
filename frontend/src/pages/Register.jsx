import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Alert, AlertDescription } from "../components/ui/alert";

import {
  UserPlus,
  Mail,
  Lock,
  User,
  Building2,
  Shield,
  AlertCircle,
  CheckCircle2
} from "lucide-react";

export default function Register() {
  const navigate = useNavigate();

  const [role, setRole] = useState("student");
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    name: "",
    organizationName: ""
  });

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = () => {
    if (!formData.email || !formData.password || !formData.confirmPassword) {
      setError("Please fill in all required fields.");
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return false;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return false;
    }

    if (role === "student" && !formData.name) {
      setError("Please enter your full name.");
      return false;
    }

    if (role === "organization" && !formData.organizationName) {
      setError("Please enter organization name.");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      await api.post("/auth/register", {
        email: formData.email,
        password: formData.password,
        role,
        name:
          role === "student"
            ? formData.name
            : role === "organization"
            ? formData.organizationName
            : undefined,
      });

      navigate("/login");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Registration failed"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6">
      <Card className="shadow-xl rounded-2xl">
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
              <UserPlus className="w-8 h-8 text-green-600" />
            </div>

            <div>
              <CardTitle className="text-2xl">Register</CardTitle>
              <CardDescription>
                Create your micro-internship account
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="w-4 h-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Role Selection */}
            <div className="space-y-2">
              <Label>Account Type</Label>

              <div className="grid gap-3">

                <label
                  className={`flex items-center gap-3 border rounded-xl p-4 cursor-pointer transition hover:bg-gray-50 ${
                    role === "student" ? "border-green-500 bg-green-50" : ""
                  }`}
                >
                  <input
                    type="radio"
                    name="role"
                    value="student"
                    checked={role === "student"}
                    onChange={() => setRole("student")}
                  />

                  <User className="w-4 text-blue-600" />

                  <div>
                    <div className="font-medium">Student</div>
                    <div className="text-xs text-gray-500">
                      Looking for micro-internships
                    </div>
                  </div>
                </label>

                <label
                  className={`flex items-center gap-3 border rounded-xl p-4 cursor-pointer transition hover:bg-gray-50 ${
                    role === "organization" ? "border-purple-500 bg-purple-50" : ""
                  }`}
                >
                  <input
                    type="radio"
                    name="role"
                    value="organization"
                    checked={role === "organization"}
                    onChange={() => setRole("organization")}
                  />

                  <Building2 className="w-4 text-purple-600" />

                  <div>
                    <div className="font-medium">Organization</div>
                    <div className="text-xs text-gray-500">
                      Posting micro-internship opportunities
                    </div>
                  </div>
                </label>

                <label
                  className={`flex items-center gap-3 border rounded-xl p-4 cursor-pointer transition hover:bg-gray-50 ${
                    role === "admin" ? "border-red-500 bg-red-50" : ""
                  }`}
                >
                  <input
                    type="radio"
                    name="role"
                    value="admin"
                    checked={role === "admin"}
                    onChange={() => setRole("admin")}
                  />

                  <Shield className="w-4 text-red-600" />

                  <div>
                    <div className="font-medium">Admin</div>
                    <div className="text-xs text-gray-500">
                      Platform administrator
                    </div>
                  </div>
                </label>
              </div>
            </div>

            {/* Name Fields */}
            {role === "student" && (
              <div className="space-y-2">
                <Label>Full Name *</Label>

                <div className="relative">
                  <User className="absolute left-3 top-3 text-gray-400 w-4" />

                  <Input
                    className="pl-10"
                    placeholder="John Doe"
                    value={formData.name}
                    onChange={(e) =>
                      handleInputChange("name", e.target.value)
                    }
                  />
                </div>
              </div>
            )}

            {role === "organization" && (
              <div className="space-y-2">
                <Label>Organization Name *</Label>

                <div className="relative">
                  <Building2 className="absolute left-3 top-3 text-gray-400 w-4" />

                  <Input
                    className="pl-10"
                    placeholder="TechVentures Inc."
                    value={formData.organizationName}
                    onChange={(e) =>
                      handleInputChange("organizationName", e.target.value)
                    }
                  />
                </div>
              </div>
            )}

            {/* Email */}
            <div className="space-y-2">
              <Label>Email</Label>

              <div className="relative">
                <Mail className="absolute left-3 top-3 text-gray-400 w-4" />

                <Input
                  className="pl-10"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={(e) =>
                    handleInputChange("email", e.target.value)
                  }
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-2">
              <Label>Password</Label>

              <div className="relative">
                <Lock className="absolute left-3 top-3 text-gray-400 w-4" />

                <Input
                  className="pl-10"
                  type="password"
                  placeholder="Min. 8 characters"
                  value={formData.password}
                  onChange={(e) =>
                    handleInputChange("password", e.target.value)
                  }
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
              <Label>Confirm Password</Label>

              <div className="relative">
                <Lock className="absolute left-3 top-3 text-gray-400 w-4" />

                <Input
                  className="pl-10"
                  type="password"
                  placeholder="Re-enter password"
                  value={formData.confirmPassword}
                  onChange={(e) =>
                    handleInputChange("confirmPassword", e.target.value)
                  }
                />
              </div>
            </div>

            <Button className="w-full" disabled={isLoading}>
              {isLoading ? "Creating Account..." : "Create Account"}
            </Button>

            <div className="text-center text-sm text-gray-600">
              Already have an account?{" "}
              <Link
                to="/login"
                className="text-blue-600 hover:underline font-medium"
              >
                Login here
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}