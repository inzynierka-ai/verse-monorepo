const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

type RequestOptions = {
  headers?: Record<string, string>;
  body?: object;
  method: string;
};

const createHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const token = localStorage.getItem('auth-token');
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
};

export const apiClient = {
  async request<T>(endpoint: string, options: RequestOptions): Promise<T> {
    const url = `${API_URL}${endpoint}`;

    const fetchOptions: RequestInit = {
      method: options.method,
      headers: {
        ...createHeaders(),
        ...(options.headers || {}),
      },
      ...(options.body ? { body: JSON.stringify(options.body) } : {}),
    };

    try {
      const response = await fetch(url, fetchOptions);

      // Handle unauthorized errors
      if (response.status === 401) {
        localStorage.removeItem('auth-token');
        // Optional: redirect to login page
        // window.location.href = '/login';
      }

      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  },

  async get<T>(endpoint: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', headers });
  },

  async post<T>(endpoint: string, body: object, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body, headers });
  },

  async put<T>(endpoint: string, body: object, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body, headers });
  },

  async delete<T>(endpoint: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE', headers });
  },
};
