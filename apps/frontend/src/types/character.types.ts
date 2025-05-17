export interface Character {
  uuid: string;
  name: string;
  description: string;
  brief_description: string;
  image_dir: string;
  role: 'player' | 'npc';
  personality_traits?: string[];
  backstory: string;
  goals: string[];
  relationship_level?: number;
}
