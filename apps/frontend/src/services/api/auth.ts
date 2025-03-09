import { useMutation } from '@tanstack/react-query';
import { apiClient } from './client';

// Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
  };
}

export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

// API functions
export const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  return apiClient.post<LoginResponse>('/auth/login', credentials);
};

export const register = async (credentials: RegisterCredentials): Promise<LoginResponse> => {
  return apiClient.post<LoginResponse>('/auth/register', credentials);
};

export const forgotPassword = async (data: ForgotPasswordRequest): Promise<{ message: string }> => {
  return apiClient.post<{ message: string }>('/auth/forgot-password', data);
};

// React Query mutations
export const useLogin = () => {
  return useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      // Store the token in localStorage on successful login
      localStorage.setItem('auth-token', data.token);
    },
  });
};

export const useRegister = () => {
  return useMutation({
    mutationFn: register,
    onSuccess: (data) => {
      // Store the token in localStorage on successful registration
      localStorage.setItem('auth-token', data.token);
    },
  });
};

export const useForgotPassword = () => {
  return useMutation({
    mutationFn: forgotPassword,
  });
};
