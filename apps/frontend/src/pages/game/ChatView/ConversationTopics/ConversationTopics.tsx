import Button from '@/common/components/Button/Button';
import { useConversationTopics } from '@/services/api/hooks/useConversationTopics';
import styles from './ConversationTopics.module.scss';

interface ConversationTopicsProps {
  characterId: string;
  sceneId: string;
  onTopicSelect: (message: string) => void;
  show: boolean;
}

const ConversationTopics = ({ characterId, sceneId, onTopicSelect, show }: ConversationTopicsProps) => {
  const { data: topicsData, isLoading, error } = useConversationTopics(characterId, sceneId);

  if (!show || isLoading || error || !topicsData?.topics?.length) {
    return null;
  }

  return (
    <div className={styles.conversationTopics}>
      <div className={styles.topicsHeader}>
        <span className={styles.headerText}>Conversation starters:</span>
      </div>
      <div className={styles.topicsList}>
        {topicsData.topics.map((topic, index) => (
          <Button
            key={index}
            variant="secondary"
            className={styles.topicButton}
            onClick={() => onTopicSelect(topic.message)}
            title={topic.message}
          >
            {topic.title}
          </Button>
        ))}
      </div>
    </div>
  );
};

export default ConversationTopics;
