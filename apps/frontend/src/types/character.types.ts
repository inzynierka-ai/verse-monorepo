export interface Character {
  id: string;
  name: string;
  avatar: string;
  relationshipLevel: number;
  threadId: string;
  description: string;
  health: number;
}

export interface Location {
  id: string;
  name: string;
  description: string;
  background: string;
  themeType?: 'library' | 'forest' | 'castle' | 'cave' | 'beach' | 'space';
}
