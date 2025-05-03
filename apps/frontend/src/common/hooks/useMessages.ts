import { useQuery } from '@tanstack/react-query';
import { Message } from '@/types/chat';
import { apiClient } from '@/services/api';

export const messagesQueryKey = (sceneId: string, characterId: string) => ['game', 'messages', sceneId, characterId];

export const useMessages = (sceneId: string, characterId: string) => {
  return useQuery<Message[]>({
    enabled: !!sceneId && !!characterId,
    queryFn: () => apiClient.get(`/messages/scenes/${sceneId}/characters/${characterId}`),
    queryKey: messagesQueryKey(sceneId, characterId),
    staleTime: Infinity,
  });
};
