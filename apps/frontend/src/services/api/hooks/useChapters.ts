import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';

export interface Chapter {
  id: number;
  story_id: number;
  title: string;
  description: string;
  prompt: string;
}

// Hook for fetching chapters for a specific story
export const useChapters = (storyId: string | number) => {
  return useQuery({
    queryKey: ['chapters', storyId],
    queryFn: async () => {
      return apiClient.get<Chapter[]>(`/api/stories/${storyId}/chapters`);
    }
  });
};

// Hook for fetching a single chapter
export const useChapter = (storyId: string | number, chapterId: string | number) => {
  return useQuery({
    queryKey: ['chapters', storyId, chapterId],
    queryFn: async () => {
      return apiClient.get<Chapter>(`/api/stories/${storyId}/chapters/${chapterId}`);
    }
  });
};

// Hook for creating a new chapter
export const useCreateChapter = (storyId: string | number) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newChapter: Omit<Chapter, 'id'>) => {
      return apiClient.post<Chapter>(`/api/stories/${storyId}/chapters`, newChapter);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chapters', storyId] });
    }
  });
};

// Hook for updating a chapter
export const useUpdateChapter = (storyId: string | number) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (chapter: Chapter) => {
      return apiClient.put<Chapter>(`/api/stories/${storyId}/chapters/${chapter.id}`, chapter);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['chapters', storyId] });
      queryClient.invalidateQueries({ queryKey: ['chapters', storyId, variables.id] });
    }
  });
};

// Hook for deleting a chapter
export const useDeleteChapter = (storyId: string | number) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (chapterId: number) => {
      return apiClient.delete<void>(`/api/stories/${storyId}/chapters/${chapterId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chapters', storyId] });
    }
  });
}; 