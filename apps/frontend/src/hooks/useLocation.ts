import { useQuery } from '@tanstack/react-query';
import { Location } from '@/types/character.types';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const fetchLocation = async (locationId: string): Promise<Location> => {
  const response = await fetch(`${BACKEND_URL}/api/locations/${locationId}`);
  if (!response.ok) throw new Error('Failed to fetch location');
  return response.json();
};

export const useLocation = (locationId: string) => {
  return useQuery({
    queryKey: ['locations', locationId],
    queryFn: () => fetchLocation(locationId),
  });
};
