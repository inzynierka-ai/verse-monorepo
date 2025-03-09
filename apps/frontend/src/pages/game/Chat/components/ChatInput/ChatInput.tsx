import { Paper, TextField, IconButton, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { ChangeEvent, FormEvent, useState } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const ChatInput = ({ onSendMessage, isLoading }: ChatInputProps) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setMessage(e.target.value);
  };

  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
      sx={{
        p: 2,
        display: 'flex',
        gap: 1,
      }}
    >
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Type a message..."
        value={message}
        onChange={handleChange}
        size="small"
        disabled={isLoading}
      />
      <IconButton type="submit" color="primary" disabled={!message.trim() || isLoading}>
        {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
      </IconButton>
    </Paper>
  );
};

export default ChatInput;
