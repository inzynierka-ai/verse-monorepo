import { Location } from './location.types';
import { Character } from './character.types';

// Describes the overall scene structure, potentially including the final description
export interface Scene {
  id?: number | string; // Optional ID if the scene itself is stored as a record
  location: Location;
  characters: Character[];
  description: string; // The final narrative description of the scene
  summary?: string; // Optional summary if provided
  // Add other relevant fields if the backend provides them for a completed scene
}
