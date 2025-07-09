const API_BASE_URL = 'https://mzhyi8cqgj06.manus.space/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'API request failed');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Auth endpoints
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async getProfile() {
    return this.request('/auth/profile');
  }

  async updateProfile(userData) {
    return this.request('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async changePassword(passwordData) {
    return this.request('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(passwordData),
    });
  }

  // Content endpoints
  async getContent(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/content${queryString ? `?${queryString}` : ''}`);
  }

  async getContentDetail(id) {
    return this.request(`/content/${id}`);
  }

  async searchContent(query) {
    return this.request(`/search?q=${encodeURIComponent(query)}`);
  }

  async getRecommendations() {
    return this.request('/recommendations');
  }

  async getGenres() {
    return this.request('/genres');
  }

  async getEpisodes(seriesId, season = null) {
    const params = season ? `?season=${season}` : '';
    return this.request(`/content/${seriesId}/episodes${params}`);
  }

  // Interaction endpoints
  async rateContent(contentId, score) {
    return this.request(`/content/${contentId}/rating`, {
      method: 'POST',
      body: JSON.stringify({ score }),
    });
  }

  async getUserRating(contentId) {
    return this.request(`/content/${contentId}/rating`);
  }

  async getContentRatings(contentId, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/content/${contentId}/ratings${queryString ? `?${queryString}` : ''}`);
  }

  async addComment(contentId, text, parentId = null) {
    return this.request(`/content/${contentId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ text, parent_id: parentId }),
    });
  }

  async getComments(contentId, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/content/${contentId}/comments${queryString ? `?${queryString}` : ''}`);
  }

  async updateWatchHistory(data) {
    return this.request('/watch-history', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getWatchHistory(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/watch-history${queryString ? `?${queryString}` : ''}`);
  }

  async addToFavorites(contentId) {
    return this.request('/favorites', {
      method: 'POST',
      body: JSON.stringify({ content_id: contentId }),
    });
  }

  async removeFromFavorites(contentId) {
    return this.request(`/favorites/${contentId}`, {
      method: 'DELETE',
    });
  }

  async getFavorites(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/favorites${queryString ? `?${queryString}` : ''}`);
  }

  async checkFavorite(contentId) {
    return this.request(`/favorites/${contentId}/check`);
  }

  async getNotifications(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/notifications${queryString ? `?${queryString}` : ''}`);
  }

  async markNotificationRead(notificationId) {
    return this.request(`/notifications/${notificationId}/read`, {
      method: 'POST',
    });
  }

  // Admin endpoints
  async getAdminStats() {
    return this.request('/admin/stats');
  }

  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/users${queryString ? `?${queryString}` : ''}`);
  }

  async getDashboardStats() {
    return this.request('/admin/dashboard/stats');
  }

  async getAllUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/users${queryString ? `?${queryString}` : ''}`);
  }

  async getUserDetail(userId) {
    return this.request(`/admin/users/${userId}`);
  }

  async toggleUserStatus(userId) {
    return this.request(`/admin/users/${userId}/toggle-status`, {
      method: 'POST',
    });
  }

  async makeUserAdmin(userId) {
    return this.request(`/admin/users/${userId}/make-admin`, {
      method: 'POST',
    });
  }

  async getAllContent(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/content/all${queryString ? `?${queryString}` : ''}`);
  }

  async createContent(contentData) {
    return this.request('/content', {
      method: 'POST',
      body: JSON.stringify(contentData),
    });
  }

  async updateContent(contentId, contentData) {
    return this.request(`/content/${contentId}`, {
      method: 'PUT',
      body: JSON.stringify(contentData),
    });
  }

  async deleteContent(contentId) {
    return this.request(`/content/${contentId}`, {
      method: 'DELETE',
    });
  }

  async toggleContentStatus(contentId) {
    return this.request(`/admin/content/${contentId}/toggle-status`, {
      method: 'POST',
    });
  }

  async toggleContentFeatured(contentId) {
    return this.request(`/admin/content/${contentId}/toggle-featured`, {
      method: 'POST',
    });
  }

  async createEpisode(seriesId, episodeData) {
    return this.request(`/content/${seriesId}/episodes`, {
      method: 'POST',
      body: JSON.stringify(episodeData),
    });
  }

  async createGenre(genreData) {
    return this.request('/genres', {
      method: 'POST',
      body: JSON.stringify(genreData),
    });
  }
}

export const apiClient = new ApiClient();

