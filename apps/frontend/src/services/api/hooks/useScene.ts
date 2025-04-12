import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';
import { Character, Location } from '@/types/character.types';
import { Message } from '@/types/chat';

export interface Scene {
  prompt: string;
  location_id: number;
  chapter_id: number;
  id: number;
  location?: Location;
  characters?: Character[];
  messages?: Message[];
}

export const useScene = (sceneId: string) => {
  return useQuery<Scene>({
    queryKey: ['scenes', sceneId],
    queryFn: async () => await apiClient.get(`/scenes/${sceneId}?resource_id=${sceneId}`),
    enabled: !!sceneId,
  });
}; 