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

export const useScenes = (chapterId: string) => {
  return useQuery<Scene[]>({
    queryKey: ['scenes', chapterId],
    queryFn: async () => await apiClient.get(`/chapters/${chapterId}/scenes?resource_id=${chapterId}`),
    enabled: !!chapterId,
  });
}; 