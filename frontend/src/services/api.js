import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchIncomeData = async (filters = {}) => {
  try {
    const params = {};
    if (filters.occupation) params.occupation = filters.occupation;
    if (filters.region) params.region = filters.region;
    if (filters.gender) params.gender = filters.gender;
    if (filters.year) params.year = filters.year;

    const response = await api.get('/income', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching income data:', error);
    return [];
  }
};

export const fetchJobAds = async (filters = {}) => {
  try {
    const params = {};
    if (filters.occupation) params.occupation = filters.occupation;
    if (filters.region) params.region = filters.region;
    params.limit = 200;  // Get more job ads

    const response = await api.get('/jobs', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching job ads:', error);
    return [];
  }
};

export const fetchJobsAggregated = async (filters = {}) => {
  try {
    const params = {};
    if (filters.occupation) params.occupation = filters.occupation;
    if (filters.region) params.region = filters.region;

    const response = await api.get('/jobs/aggregated', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching aggregated jobs:', error);
    return [];
  }
};

export const fetchOccupations = async () => {
  try {
    const response = await api.get('/occupations');
    return response.data;
  } catch (error) {
    console.error('Error fetching occupations:', error);
    return [];
  }
};

export const fetchRegions = async () => {
  try {
    const response = await api.get('/regions');
    return response.data;
  } catch (error) {
    console.error('Error fetching regions:', error);
    return [];
  }
};

export const fetchStats = async () => {
  try {
    const response = await api.get('/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    return null;
  }
};

export const fetchIncomeDispersion = async (filters = {}) => {
  try {
    const params = {};
    if (filters.occupation) params.occupation = filters.occupation;
    if (filters.year) params.year = filters.year;
    if (filters.gender) params.gender = filters.gender;

    const response = await api.get('/income/dispersion', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching income dispersion:', error);
    return [];
  }
};

export default api;
