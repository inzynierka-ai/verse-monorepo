export interface Character {
  uuid: string;
  name: string;
  description: string;
  briefDescription: string;
  image_dir: string;
  role: 'player' | 'npc';
  personalityTraits?: string[];
  backstory: string;
  goals: string[];
  relationshipLevel?: number;
}
