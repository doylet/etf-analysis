/**
 * Authentication Service for NextJS
 * 
 * Handles JWT authentication with the FastAPI backend.
 * Adapted from React POC for NextJS client/server considerations.
 */

import apiClient from './api-client';

interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface User {
  id: string;
  username: string;
  email?: string;
}

class AuthService {
  private tokenKey = 'auth_token';
  private userKey = 'user_data';

  /**
   * Login user with credentials
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await apiClient.post<LoginResponse>('/api/auth/login', credentials);
      const { access_token } = response.data;

      // Store token in localStorage (client-side only)
      if (typeof window !== 'undefined') {
        localStorage.setItem(this.tokenKey, access_token);
      }

      // Fetch user data after login
      await this.fetchUserData();

      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  /**
   * Logout user and clear stored data
   */
  logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.userKey);
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    
    const token = localStorage.getItem(this.tokenKey);
    return !!token;
  }

  /**
   * Get stored JWT token
   */
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Get stored user data
   */
  getUser(): User | null {
    if (typeof window === 'undefined') return null;
    
    const userData = localStorage.getItem(this.userKey);
    if (userData) {
      try {
        return JSON.parse(userData);
      } catch {
        return null;
      }
    }
    return null;
  }

  /**
   * Fetch user data from API and store locally
   */
  async fetchUserData(): Promise<User | null> {
    try {
      const response = await apiClient.get<User>('/api/auth/me');
      const userData = response.data;

      if (typeof window !== 'undefined') {
        localStorage.setItem(this.userKey, JSON.stringify(userData));
      }

      return userData;
    } catch (error) {
      console.error('Failed to fetch user data:', error);
      return null;
    }
  }

  /**
   * Refresh JWT token
   */
  async refreshToken(): Promise<string | null> {
    try {
      const response = await apiClient.post<LoginResponse>('/api/auth/refresh');
      const { access_token } = response.data;

      if (typeof window !== 'undefined') {
        localStorage.setItem(this.tokenKey, access_token);
      }

      return access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.logout(); // Clear invalid token
      return null;
    }
  }
}

// Export singleton instance
const authService = new AuthService();
export default authService;