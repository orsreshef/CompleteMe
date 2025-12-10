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
   * Validate answer
   */
  async validateAnswer(gameId, selectedIndex, selectedPiece) {
    return this.request('/puzzle/validate', {
      method: 'POST',
      body: JSON.stringify({
        game_id: gameId,
        selected_index: selectedIndex,
        selected_piece: selectedPiece,
      }),
    });
  }

  /**
   * Get hint
   */
  async getHint(gameId) {
    return this.request('/puzzle/hint', {
      method: 'POST',
      body: JSON.stringify({
        game_id: gameId,
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
}

const api = new ApiService();
export default api;