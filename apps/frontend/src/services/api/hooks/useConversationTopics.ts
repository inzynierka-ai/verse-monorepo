import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../client';

interface ConversationTopic {
  title: string;
  message: string;
}

interface ConversationTopicsResponse {
  topics: ConversationTopic[];
}

export const useConversationTopics = (characterId: string, sceneId: string) => {
  return useQuery({
    queryKey: ['conversation-topics', characterId, sceneId],
    queryFn: async (): Promise<ConversationTopicsResponse> => {
      return await apiClient.get<ConversationTopicsResponse>(
        `/characters/${characterId}/conversation-topics/${sceneId}`,
      );
    },
    enabled: !!characterId && !!sceneId,
    staleTime: 5 * 60 * 1000, // 5 minutes - topics don't need to be super fresh
  });
};
