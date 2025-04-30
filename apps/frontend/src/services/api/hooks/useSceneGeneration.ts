import { useCallback, useState } from 'react';
import { useWebSocket } from '@/common/hooks/webSockets/useWebSocket';
import { sendWebSocketMessage } from '@/utils/webSocket';
import { Character } from '@/types/character.types';
import { Location } from '@/types/location.types';

// Define interfaces for Scene, Location, Character based on backend expectations
// Updated based on app/schemas/story_generation.py

// Interface for the payload of SCENE_COMPLETE
interface SceneCompletePayload {
  location: Location;
  characters: Character[];
  description: string;
  summary: string;
}

// Interface for the payload of ERROR
interface ErrorPayload {
  message: string;
}

// Interface for the payload of ACTION_CHANGED
interface ActionChangedPayload {
  storyId: string;
  actions: Record<string, string>;
}

// Define message types for scene generation
interface SceneGenerationMessage {
  type:
    | 'LOCATION_ADDED'
    | 'CHARACTER_ADDED'
    | 'SCENE_COMPLETE'
    | 'ERROR'
    | 'AUTH_SUCCESS'
    | 'SCENE_START'
    | 'ACTION_CHANGED';
  // Use specific payload types based on message type
  payload: Location | Character | SceneCompletePayload | ErrorPayload | ActionChangedPayload | any;
}

// Define the state for the hook
export interface SceneGenerationState {
  status: 'idle' | 'connecting' | 'generating' | 'complete' | 'error';
  lastLocation?: Location; // Store the last added Location
  lastCharacters: Character[]; // Store all added Characters
  scene?: SceneCompletePayload; // Store the final complete scene payload
  description?: string; // Store the final scene description separately if needed
  error?: string; // Store the error message
  actions: Record<string, string>; // Track active actions by type
}

interface UseSceneGenerationProps {
  storyId: string;
  onConnectionChange?: (isConnected: boolean) => void;
  enabled?: boolean; // To control connection attempts
}

interface UseSceneGenerationReturn {
  state: SceneGenerationState;
  start: () => boolean; // Renamed from generateStory, no payload needed initially
  reset: () => void;
  isConnected: boolean;
  reconnect: () => void;
}

export const useSceneGeneration = ({
  storyId,
  onConnectionChange,
  enabled = true,
}: UseSceneGenerationProps): UseSceneGenerationReturn => {
  const [internalState, setInternalState] = useState<SceneGenerationState>({
    status: 'idle',
    lastCharacters: [],
    actions: {},
  });

  const updateState = useCallback((newState: Partial<SceneGenerationState>) => {
    setInternalState((prevState) => ({
      ...prevState,
      ...newState,
    }));
  }, []);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        // Note: We need runtime checks to determine the payload type based on message.type
        const data: SceneGenerationMessage = JSON.parse(event.data);
        console.log('Scene WS Message:', data);

        switch (data.type) {
          case 'AUTH_SUCCESS':
            // Authentication successful, no state update needed
            console.log('WebSocket authentication successful');
            break;
          case 'SCENE_START':
            // Scene generation process started
            updateState({
              status: 'generating',
            });
            break;
          case 'ACTION_CHANGED':
            // Assert payload type for ACTION_CHANGED
            const actionPayload = data.payload as ActionChangedPayload;
            updateState({
              status: 'generating',
              actions: actionPayload.actions,
            });
            break;
          case 'LOCATION_ADDED':
            // Assert payload type for LOCATION_ADDED
            const locationPayload = data.payload as Location;
            updateState({
              status: 'generating',
              lastLocation: locationPayload,
            });
            break;
          case 'CHARACTER_ADDED':
            // Assert payload type for CHARACTER_ADDED
            const characterPayload = data.payload as Character;
            setInternalState((prevState) => ({
              ...prevState,
              status: 'generating',
              lastCharacters: [...prevState.lastCharacters, characterPayload],
            }));
            break;
          case 'SCENE_COMPLETE':
            // Assert payload type for SCENE_COMPLETE
            const scenePayload = data.payload as SceneCompletePayload;
            updateState({
              status: 'complete',
              scene: scenePayload,
              description: scenePayload.description, // Also store top-level description for convenience?
              lastLocation: scenePayload.location, // Update last location from final scene
              lastCharacters: scenePayload.characters, // Update characters from final scene
              actions: {}, // Clear actions
            });
            break;
          case 'ERROR':
            // Assert payload type for ERROR
            const errorPayload = data.payload as ErrorPayload;
            updateState({
              status: 'error',
              error: errorPayload.message || 'An unknown error occurred during scene generation',
            });
            break;
          default:
            console.warn('Received unknown message type:', (data as any).type);
        }
      } catch (error) {
        console.error('Error processing scene WS message:', error);
        updateState({
          status: 'error',
          error: 'Error processing server message',
        });
      }
    },
    [updateState],
  );

  const handleOpen = useCallback(() => {
    updateState({ status: 'connecting' });
    onConnectionChange?.(true);
  }, [updateState, onConnectionChange]);

  const handleClose = useCallback(() => {
    // Optionally set status to idle or disconnected
    onConnectionChange?.(false);
  }, [onConnectionChange]);

  const wsUrl = `${import.meta.env.VITE_BACKEND_URL}/api/game/ws/stories/${storyId}/scene`;

  const { socket, isConnected, reconnect } = useWebSocket({
    url: wsUrl,
    onMessage: handleMessage,
    onOpen: handleOpen,
    onClose: handleClose,
    headers: {
      Authorization: `Bearer ${localStorage.getItem('authToken')}`,
    },
  });

  // Start generation (called when GET /latest returns 404)
  const start = useCallback(() => {
    if (!socket) {
      console.log('No WebSocket connection available, reconnecting...');
      reconnect();
      updateState({
        status: 'connecting',
        error: undefined,
      });
      return false;
    }

    updateState({
      status: 'generating',
      error: undefined,
    });

    return sendWebSocketMessage(socket, {
      type: 'START_SCENE_GENERATION',
      payload: {},
    });
  }, [socket, reconnect, updateState]);

  const reset = useCallback(() => {
    setInternalState({
      status: 'idle',
      lastCharacters: [],
      lastLocation: undefined,
      scene: undefined, // Reset scene payload
      description: undefined,
      error: undefined,
      actions: {},
    });
  }, []);

  return {
    state: internalState,
    start,
    reset,
    isConnected,
    reconnect,
  };
};
