import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  getStatus: async () => {
    const response = await api.get('/status');
    return response.data;
  },

  syncEmails: async (maxResults = 50, classify = true) => {
    const response = await api.post('/sync', {
      max_results: maxResults,
      classify,
    });
    return response.data;
  },

  syncHistorical: async (daysBack = 30) => {
    const response = await api.post('/sync/historical', {
      days_back: daysBack,
      classify: true,
    });
    return response.data;
  },

  listEmails: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.importance) params.append('importance', filters.importance);
    if (filters.category) params.append('category', filters.category);
    params.append('limit', filters.limit || 50);
    params.append('offset', filters.offset || 0);

    const response = await api.get(`/emails?${params.toString()}`);
    return response.data;
  },

  getEmail: async (emailId) => {
    const response = await api.get(`/emails/${emailId}`);
    return response.data;
  },

  getResponses: async (emailId) => {
    const response = await api.get(`/emails/${emailId}/responses`);
    return response.data;
  },

  sendEmail: async (emailId, data) => {
    const response = await api.post(`/emails/${emailId}/send`, data);
    return response.data;
  },

  improveResponse: async (emailId, draft, feedback) => {
    const response = await api.post(`/emails/${emailId}/improve`, {
      draft,
      feedback,
    });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/stats');
    return response.data;
  },

  setPreference: async (key, value) => {
    const response = await api.post(`/preferences/${key}`, value, {
      headers: { 'Content-Type': 'text/plain' },
    });
    return response.data;
  },

  getPreference: async (key, defaultValue = null) => {
    const response = await api.get(`/preferences/${key}`, {
      params: { default: defaultValue },
    });
    return response.data;
  },
};

export default api;
