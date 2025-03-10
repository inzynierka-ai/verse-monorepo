import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';

export interface Scene {
  prompt: string;
  location_id: number;
  chapter_id: number;
  id: number;
}

export const useScene = (sceneId: string) => {
  return useQuery<Scene>({
    queryKey: ['scenes', sceneId],
    queryFn: async () => await apiClient.get(`/api/scenes/${sceneId}?resource_id=${sceneId}`),
    enabled: !!sceneId,
  });
}; 