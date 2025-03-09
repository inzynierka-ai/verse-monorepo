import { Paper, Box, Typography } from '@mui/material';
import { Message } from '@/types/chat';
import RelationshipLevelIndicator from '../RelationshipLevelIndicator/RelationshipLevelIndicator';

interface MessagesProps {
  messages: Message[];
  relationshipLevel?: number;
}

const Messages = ({ messages, relationshipLevel }: MessagesProps) => {
  return (
    <Paper
      elevation={3}
      sx={{
        flex: 1,
        mb: 2,
        p: 2,
        pt: 0,
        overflow: 'auto',
        bgcolor: 'grey.100',
      }}
    >
      {relationshipLevel !== undefined && <RelationshipLevelIndicator level={relationshipLevel} />}
      {messages.map((message, index) => (
        <Box
          key={index}
          sx={{
            mb: 2,
            display: 'flex',
            flexDirection: 'column',
            alignItems: message.role === 'user' ? 'flex-end' : 'flex-start',
          }}
        >
          <Box
            sx={{
              maxWidth: '80%',
              p: 2,
              borderRadius: 2,
              bgcolor: message.role === 'user' ? 'primary.main' : 'white',
              color: message.role === 'user' ? 'white' : 'text.primary',
            }}
          >
            <Typography>{message.content}</Typography>
          </Box>
        </Box>
      ))}
    </Paper>
  );
};

export default Messages;
