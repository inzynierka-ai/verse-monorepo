import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';
import { WorldCreated, Character } from '@/services/api/hooks';

interface CreateStoryRequest {
  user_id: number;
  title: string;
  description: string;
  rules: string;
  uuid: string;
}

interface CreateStoryResponse {
  user_id: number;
  title: string;
  description: string;
  rules: string;
  uuid: string;
}

export const useCreateStory = () => {
  return useMutation({
    mutationFn: async (data: CreateStoryRequest) => {
      const response = await apiClient.post<CreateStoryResponse>('/stories', data);
      return response;
    }
  });
};

// Helper function to convert generated world and character to a story request
export const createStoryFromGeneration = (
  world: WorldCreated, 
  character: Character
): CreateStoryRequest => {
  // Create a title based on the character and world
  const title = `${character.name}'s Adventure`;

  const user_id = 1; // Placeholder for user ID, replace with actual user ID from auth token
  
  // Use the world description
  const description = world.description;
  
  // Join the rules array into a string
  const rules = world.rules.join('\n');
  
  // Generate a UUID - the backend will generate one, but we need one for the request
  const uuid = crypto.randomUUID();
  
  return {
    user_id,
    title,
    description,
    rules,
    uuid
  };
};