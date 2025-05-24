export interface Message {
  character_id: number;
  content: string;
  id: number;
  role: 'user' | 'assistant' | 'system';
  scene_id: number;
  timestamp: string;
  uuid: string;
  threadId?: string;
}

// Processing status types to match backend schema
export interface ModerationResult {
  is_flagged: boolean;
  violated_categories?: Record<string, boolean>;
  processing_time_ms?: number;
}

export interface EntityExtractionResult {
  extracted_entities: string[];
  processing_time_ms?: number;
}

export interface VectorSearchResult {
  entities_found: Array<{
    name: string;
    description: string;
    aliases: string[];
  }>;
  memories_found: Array<{
    text: string;
  }>;
  name_matches: number;
  description_matches: number;
  vector_matches: number;
  total_results: number;
  processing_time_ms?: number;
}

export interface ProcessingStatusMessage {
  type: 'processing_status';
  step: 'moderating' | 'extracting_entities' | 'searching_vectors' | 'building_prompt' | 'generating_response';
  message: string;
  debug_info?: ModerationResult | EntityExtractionResult | VectorSearchResult | Record<string, any>;
}

export interface ConversationMessage {
  type: 'chat_chunk' | 'chat_complete' | 'processing_status';
  content?: string;
  step?: ProcessingStatusMessage['step'];
  message?: string;
  debug_info?: ProcessingStatusMessage['debug_info'];
}
