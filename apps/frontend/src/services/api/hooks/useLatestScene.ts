import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';
import { Scene } from './useScene';

const getMockLatestScene = (storyId: string): Scene => ({
  id: 1,
  prompt: "You find yourself in a neon-drenched street of the megacity, where holographic billboards paint the fog with their ethereal glow",
  location_id: 1,
  chapter_id: 1,
  location: {
    id: "1",
    name: "Neo District",
    description: "A vast cyberpunk boulevard stretching into the misty distance, walls of skyscrapers adorned with massive holographic displays in neon pink, cyan, and orange. The rain-slicked ground reflects the countless advertisements, creating a mesmerizing light show that never sleeps.",
    background: "/bg.png",
    themeType: "space"
  },
  characters: [
    {
      id: "1",
      name: "Officer",
      avatar: "/avatar-transparent.png",
      description: "A stern-looking police officer in an impeccably pressed gray uniform, wearing a department badge. His sharp features and intense gaze command authority and respect.",
      relationshipLevel: 0,
      threadId: "thread_1",
      health: 100
    }
  ],
  messages: [
    {
      role: "assistant",
      content: "Halt right there, citizen. State your business in this sector. We've had reports of suspicious activity in the area.",
      threadId: "thread_1"
    },
    {
      role: "user",
      content: "I'm just passing through. I'm looking for a friend who's in town.",
      threadId: "thread_1"
    },
    {
      role: "assistant",
      content: "I'm sorry, but I can't assist with that. Please provide the name of the person you're looking for.",
      threadId: "thread_1"
    },
    {
      role: "user",
      content: "I'm just passing through. I'm looking for a friend who's in town.",
      threadId: "thread_1"
    },
    {
      role: "assistant",
      content: "I'm sorry, but I can't assist with that. Please provide the name of the person you're looking for.",
      threadId: "thread_1"
    },
    {
      role: "user",
      content: "I'm just passing through. I'm looking for a friend who's in town.",
      threadId: "thread_1"
    },
    {
      role: "assistant",
      content: "I'm asd asdq asda",
      threadId: "thread_1"
    },
  ]
});

export const useLatestScene = (storyId: string) => {
  return useQuery<Scene>({
    queryKey: ['latest-scene', storyId],
    queryFn: async () => import.meta.env.DEV ? getMockLatestScene(storyId) : await apiClient.get(`/api/stories/${storyId}/latest-scene`),
    enabled: !!storyId,
  });
};
