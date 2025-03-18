import { useQuery } from '@tanstack/react-query';
import { Character } from '@/types/character.types';
import { apiClient } from '../client';



export const useCharacter = (characterId: string) => {
  return useQuery({
    queryKey: ['characters', characterId],
    queryFn: async () => await apiClient.get(`/api/characters/${characterId}`),
  });
};
