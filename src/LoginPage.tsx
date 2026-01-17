import "./LoginPage.css";
import { Link, useNavigate } from 'react-router-dom';
import { useState } from "react";

export default function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  
  const handleLogin = async (e: React.MouseEvent) => {
    e.preventDefault();
    setError("");

    if (!username || !password) {
      setError("Please enter username and password.");
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (res.ok && data.login) {
        navigate("/home"); 
      } else {
        setError(data.message || "Login failed");
      }
    } catch (err) {
      setError("Backend server not running.");
      console.error(err);
    }
  };

  return (
    <div className="login-page">
      <div className="login-wrapper">
        <h2 className="login-title">Login to your account</h2>
        
        <div className="login-card">
          <div className="login-form">
            <div className="form-field">
              <label className="login-label">Username</label>
              <input
                type="text"
                className="login-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
              />
            </div>

            <div className="form-field">
              <label className="login-label">Password</label>
              <input 
                type="password" 
                className="login-input" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <Link to="/forgot-password" className="login-forgot">
              Forgot password?
            </Link>

            <button onClick={handleLogin} className="login-button">
              Login
            </button>

            <div className="divider">
              <span className="divider-text">or</span>
            </div>

            <Link to="/signup" className="create-account">
              Don't have an account? Create one
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}