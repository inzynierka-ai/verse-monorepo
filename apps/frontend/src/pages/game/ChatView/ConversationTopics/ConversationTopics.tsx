import Button from '@/common/components/Button/Button';
import { useConversationTopics } from '@/services/api/hooks/useConversationTopics';
import { Message } from '@/types/message.types';
import styles from './ConversationTopics.module.scss';

interface ConversationTopicsProps {
  characterId: string;
  sceneId: string;
  onTopicSelect: (message: string) => void;
  show: boolean;
  messages?: Message[];
  isStreaming?: boolean;
}

const ConversationTopics = ({
  characterId,
  sceneId,
  onTopicSelect,
  show,
  messages,
  isStreaming,
}: ConversationTopicsProps) => {
  const { data: topicsData, isLoading, error } = useConversationTopics(characterId, sceneId, messages, isStreaming);
  const isFirstConversation = !messages?.length;

  if (!show || isLoading || error || !topicsData?.topics?.length) {
    return null;
  }

  return (
    <div className={styles.conversationTopics}>
      <div className={styles.topicsHeader}>
        <span className={styles.headerText}>
          {isFirstConversation ? 'Conversation starters:' : 'Continue the conversation:'}
        </span>
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
