import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';
import { Scene } from '@/types/scene.types';

interface CompleteSceneParams {
  storyId: string;
  sceneId: string;
}

export const useCompleteScene = () => {
  const queryClient = useQueryClient();

  return useMutation<Scene, Error, CompleteSceneParams>({
    mutationFn: async ({ storyId, sceneId }: CompleteSceneParams) => {
      return await apiClient.request<Scene>(`/stories/${storyId}/scenes/${sceneId}/complete`, { method: 'PATCH' });
    },
    onSuccess: (_, { storyId }) => {
      // Invalidate the latest scene query to trigger a refetch
      queryClient.invalidateQueries({ queryKey: ['latest-scene', storyId] });
    },
  });
};
