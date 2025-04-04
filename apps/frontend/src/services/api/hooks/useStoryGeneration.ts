import { useCallback, useState } from 'react';
import { useWebSocket } from '@/common/hooks/webSockets/useWebSocket';
import { sendWebSocketMessage } from '@/utils/webSocket';

export interface WorldSettings {
  theme: string;
  genre: string;
  year: number;
  setting: string;
}

export interface PlayerCharacter {
  name: string;
  age: number;
  appearance: string;
  background: string;
}

export interface StoryGenerationRequest {
  world: WorldSettings;
  playerCharacter: PlayerCharacter;
}

export interface WorldCreated {
  description: string;
  rules: string[];
}

export interface Character {
  name: string;
  description: string;
  personalityTraits: string[];
  backstory: string;
  goals: string[];
  relationships: {
    name: string;
    level: number;
    type: string;
    backstory: string;
  }[];
  imageUrl: string;
  role: 'player' | 'npc';
}

export interface StoryGenerationMessage {
  type: 'STATUS_UPDATE' | 'WORLD_CREATED' | 'CHARACTER_CREATED' | 'INITIALIZATION_COMPLETE' | 'ERROR';
  payload: any;
}

export interface StoryGenerationState {
  status: 'idle' | 'connecting' | 'generating' | 'complete' | 'error';
  statusMessage: string;
  world?: WorldCreated;
  character?: Character;
  errorMessage?: string;
}

interface UseStoryGenerationProps {
  onStateChange?: (state: StoryGenerationState) => void;
  onConnectionChange?: (isConnected: boolean) => void;
  enabled?: boolean;
}

interface UseStoryGenerationReturn {
  state: StoryGenerationState;
  generateStory: (data: StoryGenerationRequest) => boolean;
  reset: () => void;
  isConnected: boolean;
  reconnect: () => void;
}

export const useStoryGeneration = ({
  onStateChange,
  onConnectionChange,
}: UseStoryGenerationProps = {}): UseStoryGenerationReturn => {
  // Track internal state
  const [internalState, setInternalState] = useState<StoryGenerationState>({
    status: 'idle',
    statusMessage: 'Ready to generate story',
  });

  // Create a callback to update state
  const updateState = useCallback((newState: Partial<StoryGenerationState>) => {
    const updatedState = {
      ...internalState,
      ...newState,
    };
    
    setInternalState(updatedState);
    onStateChange?.(updatedState);
    return updatedState;
  }, [internalState, onStateChange]);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data: StoryGenerationMessage = JSON.parse(event.data);
      
      switch (data.type) {
        case 'STATUS_UPDATE':
          updateState({
            status: 'generating',
            statusMessage: data.payload.message,
          });
          break;
          
        case 'WORLD_CREATED':
          updateState({
            world: data.payload,
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
  }, [updateState]);

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
    url: `${import.meta.env.VITE_BACKEND_URL}/ws/game`,
    onMessage: handleMessage,
    onOpen: handleOpen,
    onClose: handleClose,
  });

  // Generate story handler
  const generateStory = useCallback((data: StoryGenerationRequest): boolean => {
    console.log(socket)
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
      payload: data
    });
  }, [socket, reconnect, updateState]);

  // Reset state handler
  const reset = useCallback(() => {
    updateState({
      status: 'idle',
      statusMessage: 'Ready to generate story',
      world: undefined,
      character: undefined,
      errorMessage: undefined
    });
  }, [updateState]);

  return {
    state: internalState,
    generateStory,
    reset,
    isConnected,
    reconnect
  };
}; 