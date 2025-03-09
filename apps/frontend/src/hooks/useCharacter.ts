import { useQuery } from '@tanstack/react-query';
import { Character } from '@/types/character.types';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const fetchCharacter = async (characterId: string): Promise<Character> => {
  const response = await fetch(`${BACKEND_URL}/api/characters/${characterId}`);
  if (!response.ok) throw new Error('Failed to fetch character');
  return response.json();
};

export const useCharacter = (characterId: string) => {
  return useQuery({
    queryKey: ['characters', characterId],
    queryFn: () => fetchCharacter(characterId),
  });
};
