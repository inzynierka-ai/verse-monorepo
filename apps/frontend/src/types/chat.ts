export interface Message {
  role: 'user' | 'assistant';
  content: string;
  threadId: string;
}

export interface ChatMessage extends Message {
  id: string;
}

export interface MessagesResponse {
  messages: ChatMessage[];
}

export interface Action {
  name: string;
}

export interface Analysis {
  relationshipLevel: number;
  availableActions: Action[];
}
