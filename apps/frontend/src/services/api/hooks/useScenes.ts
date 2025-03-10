import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';

export interface Scene {
  prompt: string;
  location_id: number;
  chapter_id: number;
  id: number;
}

export const useScenes = (chapterId: string) => {
  return useQuery<Scene[]>({
    queryKey: ['scenes', chapterId],
    queryFn: async () => await apiClient.get(`/api/chapters/${chapterId}/scenes?resource_id=${chapterId}`),
    enabled: !!chapterId,
  });
}; 