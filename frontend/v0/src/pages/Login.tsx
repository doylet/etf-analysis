import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../api/auth';
import '../styles/Login.css';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // DEMO MODE: Skip actual auth call since endpoints not implemented (T054)
      // Store a dummy token to bypass auth checks
      localStorage.setItem('auth_token', 'demo-token');
      localStorage.setItem('auth_user', JSON.stringify({ username: username || 'demo' }));
      
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      navigate('/dashboard');
    } catch (err: any) {
      setError(
        err.response?.data?.message || 
        'Login failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>ETF Analysis Dashboard</h1>
        <p className="subtitle">Sign in to access your portfolio</p>

        <div className="demo-notice">
          <h2>🚀 Demo Mode</h2>
          <p>Authentication endpoints not yet implemented (Task T054)</p>
          <p>Enter any username (password optional) or leave blank</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username (optional)</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="demo-user"
              autoFocus
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password (optional)</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="not-required"
              disabled={loading}
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Loading Dashboard...' : 'Enter Dashboard'}
          </button>
        </form>

        <div className="login-footer">
          <p><strong>POC Testing:</strong> Click "Enter Dashboard" to continue</p>
        </div>
      </div>
    </div>
  );
}
