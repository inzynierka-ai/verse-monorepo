import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Message } from '@/types/chat';
import { analysisQueryKey } from './useAnalysis';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export const sendMessage = async (uuid: string, content: string) => {
  const response = await fetch(`${BACKEND_URL}/api/threads/${uuid}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: content }),
  });

  if (!response.ok) throw new Error('Failed to send message');

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  return reader;
};

export const useSendMessage = (uuid: string) => {
  const queryClient = useQueryClient();
  const [streamingMessage, setStreamingMessage] = useState<Message | null>(null);

  const mutation = useMutation({
    mutationFn: async (content: string) => {
      // Add user message immediately
      queryClient.setQueryData(['threads', uuid, 'messages'], (old: Message[] = []) => [
        ...old,
        { role: 'user', content },
      ]);

      // Start streaming response
      const reader = await sendMessage(uuid, content);
      let assistantMessage = '';

      // Add assistant message placeholder
      setStreamingMessage({ role: 'assistant', content: '', threadId: uuid });

      let isReading = true;
      while (isReading) {
        const { done, value } = await reader.read();
        if (done) {
          isReading = false;
          break;
        }

        // Decode the stream chunk and append to assistant message
        const chunk = new TextDecoder().decode(value);
        assistantMessage += chunk;

        // Update streaming message
        setStreamingMessage({ role: 'assistant', content: assistantMessage, threadId: uuid });
      }

      // Final update to the messages cache
      queryClient.setQueryData(['threads', uuid, 'messages'], (old: Message[] = []) => [
        ...old,
        { role: 'assistant', content: assistantMessage, threadId: uuid },
      ]);
      queryClient.invalidateQueries({ queryKey: analysisQueryKey(uuid) });

      setStreamingMessage(null);
      return assistantMessage;
    },
  });

  return {
    sendMessage: mutation.mutate,
    isLoading: mutation.isPending,
    streamingMessage,
  };
};
