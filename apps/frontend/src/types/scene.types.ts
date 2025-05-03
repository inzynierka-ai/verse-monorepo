import { Location } from './location.types';
import { Character } from './character.types';

// Describes the overall scene structure, potentially including the final description
export interface Scene {
  uuid: string;
  location: Location;
  characters: Character[];
  description: string; // The final narrative description of the scene
  summary?: string; // Optional summary if provided
  // Add other relevant fields if the backend provides them for a completed scene
}
