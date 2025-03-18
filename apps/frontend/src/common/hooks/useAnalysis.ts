import { useQuery } from '@tanstack/react-query';
import { Analysis } from '@/types/chat';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const fetchAnalysis = async (uuid: string): Promise<Analysis> => {
  const response = await fetch(`${BACKEND_URL}/api/game-master/threads/${uuid}/analysis`);
  if (!response.ok) throw new Error('Failed to fetch analysis');
  return response.json();
};

export const analysisQueryKey = (uuid: string) => ['game-master', 'threads', uuid, 'analysis'];

export const useAnalysis = (uuid: string) => {
  return useQuery<Analysis>({
    queryKey: analysisQueryKey(uuid),
    enabled: false,
    initialData: { relationshipLevel: 0, availableActions: [] },
    queryFn: () => fetchAnalysis(uuid),
  });
};
