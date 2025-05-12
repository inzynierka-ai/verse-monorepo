import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../client';

export const useCharacter = (characterId: string) => {
  return useQuery({
    queryKey: ['characters', characterId],
    queryFn: async () => await apiClient.get(`/characters/${characterId}`),
  });
};
