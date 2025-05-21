import { useCallback, useState } from 'react';
import { useWebSocket } from '@/common/hooks/webSockets/useWebSocket';
import { sendWebSocketMessage } from '@/utils/webSocket';
import { Character } from '@/types/character.types';
import { Story } from '@/types/story.types';

export interface StorySettings {
  theme: string;
  genre: string;
  year: string;
  setting: string;
}

export interface PlayerCharacter {
  name: string;
  age: string;
  appearance: string;
  background: string;
}

export interface SimpleGameInput {
  story_description: string;
  character_description: string;
}

export interface AdvancedStoryGenerationRequest {
  story: StorySettings;
  playerCharacter: PlayerCharacter;
}

export type StoryGenerationRequest = AdvancedStoryGenerationRequest | SimpleGameInput;

export interface StoryGenerationMessage {
  type: 'STATUS_UPDATE' | 'STORY_CREATED' | 'CHARACTER_CREATED' | 'INITIALIZATION_COMPLETE' | 'ERROR';
  payload: any;
}

export interface StoryGenerationState {
  status: 'idle' | 'connecting' | 'generating' | 'complete' | 'error';
  statusMessage: string;
  story?: Story;
  character?: Character;
  errorMessage?: string;
}

interface UseStoryGenerationProps {
  onConnectionChange?: (isConnected: boolean) => void;
  enabled?: boolean;
}

interface UseStoryGenerationReturn {
  state: StoryGenerationState;
  generateStory: (data: StoryGenerationRequest, isSimpleMode?: boolean) => boolean;
  generateSimpleStory: (storyDescription: string, characterDescription: string) => boolean;
  generateAdvancedStory: (data: AdvancedStoryGenerationRequest) => boolean;
  reset: () => void;
  isConnected: boolean;
  reconnect: () => void;
}

export const useStoryGeneration = ({ onConnectionChange }: UseStoryGenerationProps = {}): UseStoryGenerationReturn => {
  // Track internal state
  const [internalState, setInternalState] = useState<StoryGenerationState>({
    status: 'idle',
    statusMessage: 'Ready to generate story',
  });

  // Create a callback to update state
  const updateState = (newState: Partial<StoryGenerationState>) => {
    setInternalState((prevState) => ({
      ...prevState,
      ...newState,
    }));
  };

  // Handle incoming WebSocket messages
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const data: StoryGenerationMessage = JSON.parse(event.data);

        switch (data.type) {
          case 'STATUS_UPDATE':
            updateState({
              status: 'generating',
              statusMessage: data.payload.message,
            });
            break;

          case 'STORY_CREATED':
            updateState({
              story: data.payload,
            });
            break;

          case 'CHARACTER_CREATED':
            updateState({
              character: data.payload,
            });
            break;

          case 'INITIALIZATION_COMPLETE':
            updateState({
              status: 'complete',
              statusMessage: data.payload.message,
            });
            break;

          case 'ERROR':
            updateState({
              status: 'error',
              errorMessage: data.payload.message,
            });
            break;
        }
      } catch (error) {
        updateState({
          status: 'error',
          errorMessage: 'Error processing server message',
        });
      }
    },
    [updateState],
  );

  // Handle WebSocket open event
  const handleOpen = useCallback(() => {
    onConnectionChange?.(true);
  }, [updateState, onConnectionChange]);

  // Handle WebSocket close event
  const handleClose = useCallback(() => {
    onConnectionChange?.(false);
  }, [onConnectionChange]);

  // Initialize WebSocket connection
  const { socket, isConnected, reconnect } = useWebSocket({
    url: `${import.meta.env.VITE_BACKEND_URL}/api/game/ws`,
    onMessage: handleMessage,
    onOpen: handleOpen,
    onClose: handleClose,
    headers: {
      Authorization: `Bearer ${localStorage.getItem('authToken')}`,
    },
  });

  // Generate story handler
  const generateStory = useCallback(
    (data: StoryGenerationRequest, isSimpleMode: boolean = false): boolean => {
      if (!socket) {
        reconnect();
        return false;
      }

      updateState({
        status: 'generating',
        statusMessage: 'Sending story details...',
      });

      return sendWebSocketMessage(socket, {
        type: 'INITIALIZE_GAME',
        payload: {
          ...data,
          isSimpleMode,
        },
      });
    },
    [socket, reconnect, updateState],
  );

  // Generate story in simple mode
  const generateSimpleStory = useCallback(
    (storyDescription: string, characterDescription: string): boolean => {
      const simpleInput: SimpleGameInput = {
        story_description: storyDescription,
        character_description: characterDescription,
      };
      return generateStory(simpleInput, true);
    },
    [generateStory],
  );

  // Generate story in advanced mode
  const generateAdvancedStory = useCallback(
    (data: AdvancedStoryGenerationRequest): boolean => {
      return generateStory(data, false);
    },
    [generateStory],
  );

  // Reset state handler
  const reset = useCallback(() => {
    updateState({
      status: 'idle',
      statusMessage: 'Ready to generate story',
      story: undefined,
      character: undefined,
      errorMessage: undefined,
    });
  }, [updateState]);

  return {
    state: internalState,
    generateStory,
    generateSimpleStory,
    generateAdvancedStory,
    reset,
    isConnected,
    reconnect,
  };
}; 