import { useQuery } from '@tanstack/react-query';
import { Message } from '@/types/chat';


const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const fetchMessages = async (uuid: string): Promise<Message[]> => {
  const response = await fetch(`${BACKEND_URL}/api/scenes/${uuid}/messages`);
  if (!response.ok) throw new Error('Failed to fetch messages');
  const data = await response.json();
  return data.messages;
};

export const messagesQueryKey = (uuid: string) => ['scenes', uuid, 'messages'];

export const useMessages = (uuid: string) => {
  return useQuery<Message[]>({
    enabled: false,
    queryKey: messagesQueryKey(uuid),
    queryFn: () => fetchMessages(uuid),
  });
};
