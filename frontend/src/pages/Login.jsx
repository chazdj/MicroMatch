import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { Link } from "react-router-dom";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Alert } from "../components/ui/alert";

import { Mail, Lock, AlertCircle, LogIn } from "lucide-react";

export default function Login() {
  const { login } = useContext(AuthContext);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Login failed");
      }

      login(data.access_token, email);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 min-h-screen flex items-center justify-center">
      <Card className="w-full shadow-xl rounded-2xl">

        <CardHeader className="space-y-2">
          <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mb-2">
            <LogIn className="w-8 h-8 text-blue-600" />
          </div>

          <CardTitle className="text-2xl">Welcome Back</CardTitle>

          <CardDescription>
            Sign in to continue to MicroMatch
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-5">

          {error && (
            <Alert className="bg-red-50 text-red-700 border-red-200 flex gap-2 items-center">
              <AlertCircle className="w-4 h-4" />
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">

            <div className="space-y-2">
              <Label>Email</Label>

              <div className="relative">
                <Mail className="absolute left-3 top-3 text-gray-400 w-4" />

                <Input
                  className="pl-10"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Password</Label>

              <div className="relative">
                <Lock className="absolute left-3 top-3 text-gray-400 w-4" />

                <Input
                  className="pl-10"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <Button className="w-full" disabled={loading}>
              {loading ? "Signing in..." : "Login"}
            </Button>
          </form>

          <div className="text-center text-sm text-gray-600 pt-2">
            Don’t have an account?{" "}
            <Link
              to="/register"
              className="text-blue-600 font-medium hover:underline"
            >
              Register
            </Link>
          </div>

        </CardContent>
      </Card>
    </div>
  );
}