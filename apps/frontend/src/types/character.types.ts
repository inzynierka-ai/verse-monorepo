export interface CharacterRelationship {
  name: string;
  level: number;
  type: string;
  backstory: string;
}

export interface Character {
  uuid: string;
  name: string;
  description: string;
  imageUrl: string;
  role: 'player' | 'npc';
  personalityTraits?: string[];
  backstory: string;
  goals: string[];
  relationships: CharacterRelationship[];
}
