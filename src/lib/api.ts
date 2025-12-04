/**
 * API client for FastAPI backend
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = {
  async generateJobPosting(data: {
    jobTitle: string;
    careerLevel: string;
    location: string;
    department: string;
    keySkills?: string;
  }) {
    const response = await fetch(`${API_BASE_URL}/api/generate-job-posting`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return response.json();
  },

  async approvePosting(data: {
    naturalPosting: string;
    structuredData: string;
    originalInput: any;
  }) {
    const response = await fetch(`${API_BASE_URL}/api/approve-posting`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(error.detail || error.error || `HTTP ${response.status}`);
    }

    return response.json();
  },

  async getJobPostings() {
    const response = await fetch(`${API_BASE_URL}/api/job-postings`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(error.detail || error.error || `HTTP ${response.status}`);
    }

    return response.json();
  },
};

