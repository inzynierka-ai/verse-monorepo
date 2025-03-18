import { useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from './webSockets/useWebSocket';
import { sendWebSocketMessage } from '@/utils/webSocket';
import { Message, Analysis } from '@/types/chat';
import { messagesQueryKey } from './useMessages';
import { analysisQueryKey } from './useAnalysis';

// Types for scene-specific messages
interface SceneMessage {
  type: 'chat_chunk' | 'chat_complete' | 'analysis';
  content?: string;
  analysis?: Analysis;
}

interface UseSceneProps {
  sceneId: string;
  onConnectionChange?: (isConnected: boolean) => void;
}

interface UseSceneReturn {
  sendMessage: (content: string) => boolean;
  isConnected: boolean;
  reconnect: () => void;
}

export const useScene = ({ sceneId, onConnectionChange }: UseSceneProps): UseSceneReturn => {
  const queryClient = useQueryClient();

  // Handle incoming messages from WebSocket
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const message: SceneMessage = JSON.parse(event.data);
        switch (message.type) {
          case 'chat_chunk': {
            if (!message.content) break;
            queryClient.setQueryData(messagesQueryKey(sceneId), (old: Message[] = []) => {
              const messages = [...old];
              const lastMessage = messages[messages.length - 1];
              if (lastMessage?.role === 'assistant') {
                messages[messages.length - 1] = {
                  ...lastMessage,
                  content: lastMessage.content + message.content,
                };
                return messages;
              }
              return [
                ...messages,
                { role: 'assistant', content: message.content, threadId: sceneId },
              ];
            });
            break;
          }
          case 'analysis':
            if (message.analysis) {
              queryClient.setQueryData(analysisQueryKey(sceneId), message.analysis);
            }
            break;
          case 'chat_complete':
            break;
        }
      } catch (error) {
        console.error(error);
      }
    },
    [queryClient, sceneId],
  );

  // Handle WebSocket connection changes
  const handleOpen = useCallback(() => {
    onConnectionChange?.(true);
  }, [onConnectionChange]);

  const handleClose = useCallback(() => {
    onConnectionChange?.(false);
  }, [onConnectionChange]);
  
  // Initialize WebSocket connection with enabled flag based on sceneId
  const { socket, isConnected, reconnect } = useWebSocket({
    url: `${import.meta.env.VITE_BACKEND_URL}/api/scenes/${sceneId}`,
    onMessage: handleMessage,
    onOpen: handleOpen,
    onClose: handleClose,
    enabled: !!sceneId
  });

  // Send message handler
  const sendMessage = useCallback(
    (content: string) => {
      // Don't send if no valid sceneId or socket
      if (!sceneId || !socket) return false;
      
      // Optimistically update messages cache
      queryClient.setQueryData(messagesQueryKey(sceneId), (old: Message[] = []) => [
        ...old,
        { role: 'user', content, threadId: sceneId },
      ]);

      // Send message through WebSocket
      return sendWebSocketMessage(socket, {
        type: 'message',
        content,
        sceneId,
      });
    },
    [socket, sceneId, queryClient],
  );

  return {
    sendMessage,
    isConnected,
    reconnect,
  };
};
