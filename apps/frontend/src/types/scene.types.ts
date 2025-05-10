import { Location } from './location.types';
import { Character } from './character.types';
import { Message } from './message.types';
// Describes the overall scene structure, potentially including the final description
export interface Scene {
  uuid: string;
  location: Location;
  characters: Character[];
  description: string; // The final narrative description of the scene
  summary?: string; // Optional summary if provided
  messages: Message[];
  // Add other relevant fields if the backend provides them for a completed scene
}
