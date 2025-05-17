export interface Message {
  character_id: number;
  content: string;
  id: number;
  role: 'user' | 'assistant';
  scene_id: number;
  timestamp: string;
  uuid: string;
}
