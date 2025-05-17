import { useQuery } from '@tanstack/react-query';
import { Location } from '@/types/location.types';
import { apiClient } from '../client';

export const useLocation = (locationId: string) => {
  return useQuery<Location>({
    queryKey: ['locations', locationId],
    queryFn: async () => await apiClient.get(`/locations/${locationId}`),
    enabled: !!locationId,
  });
};
