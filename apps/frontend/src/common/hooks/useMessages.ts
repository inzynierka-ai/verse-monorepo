import { useQuery } from '@tanstack/react-query';
import { Message } from '@/types/chat';

export const messagesQueryKey = (uuid: string) => ['scenes', uuid, 'messages'];

export const useMessages = (uuid: string, initialMessages?: Message[]) => {
  return useQuery<Message[]>({
    enabled: !!uuid,
    queryKey: messagesQueryKey(uuid),    
    initialData: initialMessages,
    staleTime: Infinity,
  });
};
