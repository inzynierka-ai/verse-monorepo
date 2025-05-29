import { useCallback, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from '@/common/hooks/webSockets/useWebSocket';
import { sendWebSocketMessage } from '@/utils/webSocket';
import { Message, ConversationMessage, ProcessingStatusMessage } from '@/types/message.types';
import { messagesQueryKey } from './useMessages';

interface UseConversationProps {
  sceneId: string;
  characterId: string;
  onConnectionChange?: (isConnected: boolean) => void;
  onStreamingStateChange?: (isStreaming: boolean) => void;
  onProcessingStatusChange?: (status: ProcessingStatusMessage | null) => void;
}

interface UseConversationReturn {
  sendMessage: (content: string) => boolean;
  isConnected: boolean;
  isStreaming: boolean;
  reconnect: () => void;
  processingStatus: ProcessingStatusMessage | null;
}

export const useConversation = ({
  sceneId,
  characterId,
  onConnectionChange,
  onStreamingStateChange,
  onProcessingStatusChange,
}: UseConversationProps): UseConversationReturn => {
  const queryClient = useQueryClient();
  const [isStreaming, setIsStreaming] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatusMessage | null>(null);

  // Handle incoming messages from WebSocket
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const message: ConversationMessage = JSON.parse(event.data);
        switch (message.type) {
          case 'chat_chunk': {
            if (!message.content) break;

            if (!isStreaming) {
              setIsStreaming(true);
              onStreamingStateChange?.(true);
            }

            // Clear processing status when we start receiving chunks
            if (processingStatus) {
              setProcessingStatus(null);
              onProcessingStatusChange?.(null);
            }

            queryClient.setQueryData(messagesQueryKey(sceneId, characterId), (old: Message[] = []) => {
              const messages = [...old];
              const lastMessage = messages[messages.length - 1];
              if (lastMessage?.role === 'assistant') {
                messages[messages.length - 1] = {
                  ...lastMessage,
                  content: lastMessage.content + message.content,
                };
                return messages;
              }
              return [...messages, { role: 'assistant', content: message.content, threadId: sceneId }];
            });
            break;
          }
          case 'chat_complete':
            setIsStreaming(false);
            onStreamingStateChange?.(false);
            setProcessingStatus(null);
            onProcessingStatusChange?.(null);
            break;
          case 'processing_status': {
            const statusMessage: ProcessingStatusMessage = {
              type: 'processing_status',
              step: message.step!,
              message: message.message!,
              debug_info: message.debug_info,
            };
            setProcessingStatus(statusMessage);
            onProcessingStatusChange?.(statusMessage);
            break;
          }
        }
      } catch (error) {
        console.error(error);
      }
    },
    [
      queryClient,
      sceneId,
      characterId,
      isStreaming,
      onStreamingStateChange,
      onProcessingStatusChange,
      processingStatus,
    ],
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
    url: `${import.meta.env.VITE_BACKEND_URL}/api/game/ws/scenes/${sceneId}/characters/${characterId}`,
    onMessage: handleMessage,
    onOpen: handleOpen,
    onClose: handleClose,
    headers: {
      Authorization: `Bearer ${localStorage.getItem('authToken')}`,
    },
  });

  // Send message handler
  const sendMessage = useCallback(
    (content: string) => {
      // Don't send if no valid sceneId or socket
      if (!sceneId || !socket) return false;

      // Get current messages from cache for context
      const currentMessages = queryClient.getQueryData<Message[]>(messagesQueryKey(sceneId, characterId)) || [];

      // Optimistically update messages cache
      const updatedMessages = [...currentMessages, { role: 'user', content, threadId: sceneId }];

      queryClient.setQueryData(messagesQueryKey(sceneId, characterId), updatedMessages);

      // Send message through WebSocket with all required fields from ClientMessage model
      const success = sendWebSocketMessage(socket, {
        sceneId,
        characterId,
        messages: updatedMessages,
      });

      return success;
    },
    [socket, sceneId, characterId, queryClient],
  );

  return {
    sendMessage,
    isConnected,
    isStreaming,
    reconnect,
    processingStatus,
  };
};
