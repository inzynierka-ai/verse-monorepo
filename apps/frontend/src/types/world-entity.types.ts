export interface WorldEntity {
  id: number;
  story_id: number;
  name: string;
  canonical_description: string;
  embedding?: number[];
  aliases: string[];
  discovered_in_scene?: string;
  created_at?: string;
}
