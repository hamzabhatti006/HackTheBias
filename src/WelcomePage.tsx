import "./WelcomePage.css";
import { useNavigate } from 'react-router-dom';

export default function WelcomePage() {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate("/login");
  };

  return (
    <div className="welcome-page">
      <div className="welcome-container">
        <div className="welcome-content">
          <h1 className="welcome-title">Welcome to HackTheBias</h1>
          <p className="welcome-subtitle">Your journey to unbiased learning starts here</p>
          <button 
            className="welcome-login-button" 
            onClick={handleLoginClick}
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
}
