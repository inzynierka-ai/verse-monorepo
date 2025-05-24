import { useState } from 'react';
import {
  ProcessingStatusMessage,
  ModerationResult,
  EntityExtractionResult,
  VectorSearchResult,
} from '@/types/message.types';
import styles from './ProcessingIndicator.module.scss';

interface ProcessingIndicatorProps {
  status: ProcessingStatusMessage | null;
  isVisible: boolean;
}

const ProcessingIndicator: React.FC<ProcessingIndicatorProps> = ({ status, isVisible }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isVisible || !status) {
    return null;
  }

  const getStepIcon = (step: ProcessingStatusMessage['step']) => {
    switch (step) {
      case 'moderating':
        return '🛡️';
      case 'extracting_entities':
        return '🔍';
      case 'searching_vectors':
        return '🧠';
      case 'building_prompt':
        return '📝';
      case 'generating_response':
        return '💭';
      default:
        return '⚙️';
    }
  };

  const getStepDescription = (step: ProcessingStatusMessage['step']) => {
    switch (step) {
      case 'moderating':
        return 'Content Safety Check';
      case 'extracting_entities':
        return 'Entity Extraction';
      case 'searching_vectors':
        return 'Context Search';
      case 'building_prompt':
        return 'Building Context';
      case 'generating_response':
        return 'Generating Response';
      default:
        return 'Processing';
    }
  };

  const renderDebugInfo = () => {
    if (!status.debug_info) return null;

    // Type guard functions
    const isModerationResult = (info: any): info is ModerationResult => {
      return info && typeof info.is_flagged === 'boolean';
    };

    const isEntityExtractionResult = (info: any): info is EntityExtractionResult => {
      return info && Array.isArray(info.extracted_entities);
    };

    const isVectorSearchResult = (info: any): info is VectorSearchResult => {
      return info && Array.isArray(info.entities_found) && Array.isArray(info.memories_found);
    };

    if (isModerationResult(status.debug_info)) {
      const moderation = status.debug_info;
      return (
        <div className={styles.debugSection}>
          <h4>Moderation Results</h4>
          <div className={styles.debugItem}>
            <span className={styles.label}>Status:</span>
            <span className={moderation.is_flagged ? styles.flagged : styles.clean}>
              {moderation.is_flagged ? 'Flagged' : 'Clean'}
            </span>
          </div>
          {moderation.violated_categories && Object.keys(moderation.violated_categories).length > 0 && (
            <div className={styles.debugItem}>
              <span className={styles.label}>Violations:</span>
              <div className={styles.violationsList}>
                {Object.entries(moderation.violated_categories).map(([category, violated]) =>
                  violated ? (
                    <span key={category} className={styles.violation}>
                      {category}
                    </span>
                  ) : null,
                )}
              </div>
            </div>
          )}
          {moderation.processing_time_ms && (
            <div className={styles.debugItem}>
              <span className={styles.label}>Processing Time:</span>
              <span>{moderation.processing_time_ms.toFixed(1)}ms</span>
            </div>
          )}
        </div>
      );
    }

    if (isEntityExtractionResult(status.debug_info)) {
      const extraction = status.debug_info;
      return (
        <div className={styles.debugSection}>
          <h4>Entity Extraction</h4>
          <div className={styles.debugItem}>
            <span className={styles.label}>Entities Found:</span>
            <span>{extraction.extracted_entities.length}</span>
          </div>
          {extraction.extracted_entities.length > 0 && (
            <div className={styles.debugItem}>
              <span className={styles.label}>Entities:</span>
              <div className={styles.entitiesList}>
                {extraction.extracted_entities.map((entity, index) => (
                  <span key={index} className={styles.entity}>
                    {entity}
                  </span>
                ))}
              </div>
            </div>
          )}
          {extraction.processing_time_ms && (
            <div className={styles.debugItem}>
              <span className={styles.label}>Processing Time:</span>
              <span>{extraction.processing_time_ms.toFixed(1)}ms</span>
            </div>
          )}
        </div>
      );
    }

    if (isVectorSearchResult(status.debug_info)) {
      const search = status.debug_info;
      return (
        <div className={styles.debugSection}>
          <h4>Vector Search Results</h4>
          <div className={styles.searchStats}>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Name Matches:</span>
              <span className={styles.statValue}>{search.name_matches}</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Description Matches:</span>
              <span className={styles.statValue}>{search.description_matches}</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Vector Matches:</span>
              <span className={styles.statValue}>{search.vector_matches}</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Total Results:</span>
              <span className={styles.statValue}>{search.total_results}</span>
            </div>
          </div>

          {search.entities_found.length > 0 && (
            <div className={styles.resultsSection}>
              <h5>Entities Found</h5>
              {search.entities_found.map((entity, index) => (
                <div key={index} className={styles.resultItem}>
                  <div className={styles.resultName}>{entity.name}</div>
                  <div className={styles.resultDescription}>{entity.description}</div>
                  {entity.aliases.length > 0 && (
                    <div className={styles.resultAliases}>Aliases: {entity.aliases.join(', ')}</div>
                  )}
                </div>
              ))}
            </div>
          )}

          {search.memories_found.length > 0 && (
            <div className={styles.resultsSection}>
              <h5>Memories Found</h5>
              {search.memories_found.map((memory, index) => (
                <div key={index} className={styles.resultItem}>
                  <div className={styles.memoryText}>{memory.text}</div>
                </div>
              ))}
            </div>
          )}

          {search.processing_time_ms && (
            <div className={styles.debugItem}>
              <span className={styles.label}>Processing Time:</span>
              <span>{search.processing_time_ms.toFixed(1)}ms</span>
            </div>
          )}
        </div>
      );
    }

    return null;
  };

  return (
    <div className={styles.processingIndicator}>
      <div className={styles.statusBar}>
        <div className={styles.statusContent}>
          <div className={styles.statusIcon}>
            <span className={styles.icon}>{getStepIcon(status.step)}</span>
            <div className={styles.spinner}></div>
          </div>
          <div className={styles.statusText}>
            <div className={styles.stepName}>{getStepDescription(status.step)}</div>
            <div className={styles.statusMessage}>{status.message}</div>
          </div>
        </div>
        {status.debug_info && (
          <button className={styles.debugToggle} onClick={() => setIsExpanded(!isExpanded)} aria-expanded={isExpanded}>
            {isExpanded ? '▼' : '▶'} Debug
          </button>
        )}
      </div>

      {isExpanded && status.debug_info && <div className={styles.debugInfo}>{renderDebugInfo()}</div>}
    </div>
  );
};

export default ProcessingIndicator;
