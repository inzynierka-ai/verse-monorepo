import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';
import { StoryCreated, Character } from '@/services/api/hooks';

interface CreateStoryRequest {
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
    },
  });
};

// Helper function to convert generated story and character to a story request
export const createStoryFromGeneration = (story: StoryCreated, character: Character): CreateStoryRequest => {
  // Create a title based on the character and story
  const title = `${character.name}'s Adventure`;

  // Use the story description
  const description = story.description;

  // Join the rules array into a string
  const rules = story.rules.join('\n');

  // Generate a UUID - the backend will generate one, but we need one for the request
  const uuid = crypto.randomUUID();

  return {
    title,
    description,
    rules,
    uuid,
  };
};