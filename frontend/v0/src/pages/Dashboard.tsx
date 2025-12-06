import { useNavigate } from 'react-router-dom';
import PortfolioSummary from '../components/PortfolioSummary';
import authService from '../api/auth';
import '../styles/Dashboard.css';

export default function Dashboard() {
  const navigate = useNavigate();
  const user = authService.getUser();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>ETF Analysis Dashboard</h1>
          <div className="user-section">
            {user && <span className="username">Welcome, {user.username}</span>}
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <PortfolioSummary />
      </main>

      <footer className="dashboard-footer">
        <p>ETF Analysis POC - Phase 8 (US6)</p>
        <p>Backend API: FastAPI | Frontend: React + TypeScript + Vite</p>
      </footer>
    </div>
  );
}
