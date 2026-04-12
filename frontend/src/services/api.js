/**
 * API Service
 * Handles all communication with the backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Make HTTP request
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
      // credentials:'include' sends/receives HTTP-only JWT cookies automatically
      credentials: 'include',
    };

    const config = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ API Error (${endpoint}):`, error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    return this.request('/health');
  }

  /**
   * Get configuration
   */
  async getConfig() {
    return this.request('/config');
  }

  /**
   * Create new puzzle
   */
  async createPuzzle(data) {
    return this.request('/puzzle/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Validate answer — placements is [{zone_index, piece}, ...]
   */
  async validateAnswer(gameId, placements) {
    return this.request('/puzzle/validate', {
      method: 'POST',
      body: JSON.stringify({
        game_id: gameId,
        placements,
      }),
    });
  }

  /**
   * Get hint
   */
  async getHint(gameId, zoneIndex) {
    return this.request('/puzzle/hint', {
      method: 'POST',
      body: JSON.stringify({
        game_id: gameId,
        zone_index: zoneIndex,
      }),
    });
  }

  /**
   * Get statistics
   */
  async getStats() {
    return this.request('/stats');
  }

  /**
   * Cleanup game
   */
  async cleanupGame(gameId) {
    return this.request('/puzzle/cleanup', {
      method: 'POST',
      body: JSON.stringify({
        game_id: gameId,
      }),
    });
  }

  // ── Auth ────────────────────────────────────────────────────────────────

  /**
   * Register a new account
   */
  async register(username, email, password, avatarId = 1) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password, avatar_id: avatarId }),
    });
  }

  /**
   * Log in — sets HTTP-only JWT cookies via the browser
   */
  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  /**
   * Log out — clears JWT cookies
   */
  async logout() {
    return this.request('/auth/logout', { method: 'POST' });
  }

  /**
   * Get the currently authenticated user's profile
   */
  async getMe() {
    return this.request('/auth/me');
  }

  /**
   * Refresh the access token using the refresh cookie
   */
  async refreshToken() {
    return this.request('/auth/refresh', { method: 'POST' });
  }

  /**
   * Get the current user's game history
   */
  async getHistory() {
    return this.request('/auth/history');
  }

  /**
   * Update the current user's avatar
   */
  async updateAvatar(avatarId) {
    return this.request('/auth/update-avatar', {
      method: 'PATCH',
      body: JSON.stringify({ avatar_id: avatarId }),
    });
  }

  /**
   * Change the current user's password
   */
  async changePassword(currentPassword, newPassword) {
    return this.request('/auth/change-password', {
      method: 'PATCH',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
  }

  /**
   * Permanently delete the current user's account
   */
  async deleteAccount(password) {
    return this.request('/auth/delete-account', {
      method: 'DELETE',
      body: JSON.stringify({ password }),
    });
  }
}

const api = new ApiService();
export default api;
