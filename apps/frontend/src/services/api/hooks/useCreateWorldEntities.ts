import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';
import { WorldEntity } from '@/types/world-entity.types';

interface CreateWorldEntitiesParams {
  sceneUuid: string;
}

export const useCreateWorldEntities = () => {
  const queryClient = useQueryClient();

  return useMutation<WorldEntity[], Error, CreateWorldEntitiesParams>({
    mutationFn: async ({ sceneUuid }: CreateWorldEntitiesParams) => {
      return await apiClient.post<WorldEntity[]>('/world_entities/', { sceneUuid });
    },
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['world-entities'] });
    },
  });
};
