import React, { useState } from 'react';
import { Box, TextField, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const InterviewChat = ({ onSendMessage, disabled }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <TextField
        fullWidth
        multiline
        maxRows={3}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="输入你的回答，按Enter发送..."
        disabled={disabled}
        size="small"
      />
      <Button
        variant="contained"
        onClick={handleSend}
        disabled={!input.trim() || disabled}
        sx={{ minWidth: '80px' }}
      >
        <SendIcon />
      </Button>
    </Box>
  );
};

export default InterviewChat;
