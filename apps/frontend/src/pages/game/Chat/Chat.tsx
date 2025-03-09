import { Box, Container, Alert } from '@mui/material';
import Messages from './components/Messages/Messages';
import ChatInput from './components/ChatInput/ChatInput';
import { useMessages } from '@/hooks/useMessages';
import { useAnalysis } from '@/hooks/useAnalysis';
import { useScene } from '@/hooks/useScene';

interface ChatViewProps {
  uuid: string;
}

const Chat = ({ uuid }: ChatViewProps) => {
  const { data: messages = [] } = useMessages(uuid);
  const { data: analysis } = useAnalysis(uuid);
  const { sendMessage, isConnected } = useScene({
    sceneId: uuid,
  });

  return (
    <Container maxWidth="sm">
      <Box sx={{ height: 'calc(100dvh - 48px)', py: 2, display: 'flex', flexDirection: 'column' }}>
        {!isConnected && (
          <Alert severity="warning">Connection lost. Attempting to reconnect...</Alert>
        )}
        <Messages messages={messages} relationshipLevel={analysis?.relationshipLevel} />
        <ChatInput onSendMessage={sendMessage} isLoading={!isConnected} />
      </Box>
    </Container>
  );
};

export default Chat;
