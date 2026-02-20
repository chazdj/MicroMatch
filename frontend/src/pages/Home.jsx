import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

/**
 * Home page / dashboard shown after login.
 * Displays user email and allows logout.
 */
export default function Home() {
  const { email, logout } = useContext(AuthContext);

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Welcome to MicroMatch!</h1>
      <p>Logged in as: <strong>{email}</strong></p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}