import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';

interface CreateStoryRequest {
  title: string;
  description: string;
  rules: string;
  uuid: string;
}

interface CreateStoryResponse {
  user_id: number;
  title: string;
  description: string;
  rules: string;
  uuid: string;
}

export const useCreateStory = () => {
  return useMutation({
    mutationFn: async (data: CreateStoryRequest) => {
      const response = await apiClient.post<CreateStoryResponse>('/stories', data);
      return response;
    },
  });
};

