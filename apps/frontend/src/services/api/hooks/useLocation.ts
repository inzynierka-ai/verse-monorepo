import { useQuery } from '@tanstack/react-query';
import { Location } from '@/types/character.types';
import { apiClient } from '../client';



export const useLocation = (locationId: string) => {
  return useQuery({
    queryKey: ['locations', locationId],
    queryFn: async () => await apiClient.get(`/locations/${locationId}`),
    enabled: !!locationId,
  });
};
