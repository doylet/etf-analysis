/**
 * Authentication Service
 * 
 * Handles user authentication, JWT token storage, and auth state.
 */

import apiClient from './client';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: {
    username: string;
    email?: string;
  };
}

class AuthService {
  private readonly TOKEN_KEY = 'auth_token';
  private readonly USER_KEY = 'auth_user';

  /**
   * Login with username and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>('/api/auth/login', credentials);
      const { access_token, user } = response.data;
      
      // Store token and user info
      localStorage.setItem(this.TOKEN_KEY, access_token);
      if (user) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
      }
      
      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  /**
   * Logout - clear auth data
   */
  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  /**
   * Get stored JWT token
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Get stored user info
   */
  getUser(): { username: string; email?: string } | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Refresh token (if endpoint exists)
   */
  async refreshToken(): Promise<string> {
    try {
      const response = await apiClient.post<AuthResponse>('/api/auth/refresh');
      const { access_token } = response.data;
      localStorage.setItem(this.TOKEN_KEY, access_token);
      return access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.logout();
      throw error;
    }
  }
}

export default new AuthService();
