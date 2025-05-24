import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../client';
import { Message } from '@/types/message.types';

interface ConversationTopic {
  title: string;
  message: string;
}

interface ConversationTopicsResponse {
  topics: ConversationTopic[];
}

export const useConversationTopics = (
  characterId: string,
  sceneId: string,
  messages?: Message[],
  isStreaming?: boolean,
) => {
  const lastMessage = messages?.[messages.length - 1];
  const shouldFetchTopics = !messages?.length || (lastMessage?.role === 'assistant' && !isStreaming);

  let lastAssistantMessageIndex = -1;
  if (messages?.length) {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'assistant') {
        lastAssistantMessageIndex = i;
        break;
      }
    }
  }

  return useQuery({
    queryKey: ['conversation-topics', characterId, sceneId, lastAssistantMessageIndex],
    queryFn: async (): Promise<ConversationTopicsResponse> => {
      return await apiClient.request<ConversationTopicsResponse>(
        `/characters/${characterId}/conversation-topics/${sceneId}`,
        {
          method: 'POST',
          ...(messages && { body: messages }),
        },
      );
    },
    enabled: !!characterId && !!sceneId && shouldFetchTopics,
    staleTime: 1 * 60 * 1000,
  });
};
