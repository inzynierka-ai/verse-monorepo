import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';
import { Scene } from '@/types/scene.types';

export const useLatestScene = (storyId: string) => {
  return useQuery<Scene>({
    queryKey: ['latest-scene', storyId],
    queryFn: async () => await apiClient.get(`/stories/${storyId}/scene/latest`),
    enabled: !!storyId,
  });
};
