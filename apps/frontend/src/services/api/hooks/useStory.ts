import { useQuery } from '@tanstack/react-query';
import { Story } from '@/types/story.types';
import { apiClient } from '@/services/api/client';

const fetchStories = async (): Promise<Story[]> => {
  const response = await apiClient.get<Story[]>('/stories');
  return response;
};

export const useStories = () => {
  return useQuery({
    queryKey: ['stories'],
    queryFn: fetchStories,
  });
};