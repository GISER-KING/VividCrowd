import React, { useState, useEffect, useRef } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { 
  Box, Container, Paper, TextField, IconButton, Typography, 
  Avatar, Drawer, List, ListItem, ListItemAvatar, ListItemText, Divider
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import GroupIcon from '@mui/icons-material/Group';
import MenuIcon from '@mui/icons-material/Menu';
import { CONFIG } from './config';

function App() {
  const [messageHistory, setMessageHistory] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [agents, setAgents] = useState([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [typingStatus, setTypingStatus] = useState('');
  const incomingBuffer = useRef({});
  const bottomRef = useRef(null);

  // 获取群成员列表
  useEffect(() => {
    fetch('/api/agents')
      .then(res => res.json())
      .then(data => setAgents(data))
      .catch(err => console.error("Failed to fetch agents:", err));
  }, []);

  // WebSocket 连接
  const { sendMessage, lastMessage, readyState } = useWebSocket(CONFIG.WS_URL, {
    shouldReconnect: (closeEvent) => true,
  });

  // 处理收到的消息
  useEffect(() => {
    if (lastMessage !== null) {
      try {
        const data = JSON.parse(lastMessage.data);
        handleIncomingMessage(data);
      } catch (e) {
        console.error("Parse error", e);
      }
    }
  }, [lastMessage]);

  // 滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messageHistory, typingStatus]);

  const handleIncomingMessage = (data) => {
    const { type, sender, content } = data;

    if (type === 'stream_start') {
      incomingBuffer.current[sender] = '';
      setTypingStatus(`${sender} 正在输入...`);
      
    } else if (type === 'stream_chunk') {
      if (incomingBuffer.current[sender] !== undefined) {
        incomingBuffer.current[sender] += content;
      }
      
    } else if (type === 'stream_end') {
      const fullContent = incomingBuffer.current[sender];
      delete incomingBuffer.current[sender];
      setTypingStatus('');

      if (fullContent && fullContent !== "...") {
          setMessageHistory((prev) => [
            ...prev,
            {
              id: Date.now() + Math.random(),
              sender: sender,
              content: fullContent,
              isUser: false,
              streaming: false
            }
          ]);
      }
    }
  };

  const handleSendMessage = () => {
    if (inputMessage.trim() === '') return;
    
    sendMessage(inputMessage);

    setMessageHistory(prev => [
      ...prev,
      {
        id: Date.now(),
        sender: '你',
        content: inputMessage,
        isUser: true,
        streaming: false
      }
    ]);
    
    setInputMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const toggleDrawer = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setIsDrawerOpen(open);
  };

  const listAgents = () => (
    <Box
      sx={{ width: 280 }}
      role="presentation"
      onClick={toggleDrawer(false)}
      onKeyDown={toggleDrawer(false)}
    >
      <Box sx={{ p: 2, bgcolor: '#f5f5f5' }}>
        <Typography variant="h6">群成员 ({agents.length})</Typography>
      </Box>
      <List>
        {agents.map((agent) => (
          <React.Fragment key={agent.id}>
            <ListItem alignItems="flex-start">
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: CONFIG.AVATAR_COLORS[agent.name] || CONFIG.DEFAULT_AVATAR_COLOR }}>
                  {agent.name[0]}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Typography variant="subtitle1" component="span" sx={{ fontWeight: 'bold' }}>
                    {agent.name}
                  </Typography>
                }
                secondary={
                  <React.Fragment>
                    <Typography
                      sx={{ display: 'inline' }}
                      component="span"
                      variant="body2"
                      color="text.primary"
                    >
                      {agent.occupation}
                    </Typography>
                    <br />
                    <Typography variant="caption" color="text.secondary">
                      {agent.personality} | 兴趣: {agent.interests}
                    </Typography>
                  </React.Fragment>
                }
              />
            </ListItem>
            <Divider variant="inset" component="li" />
          </React.Fragment>
        ))}
      </List>
    </Box>
  );

  return (
    <Container maxWidth="sm" sx={{ height: '100vh', display: 'flex', flexDirection: 'column', p: 0 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 2, bgcolor: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'space-between', zIndex: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <GroupIcon sx={{ mr: 1, color: '#555' }} />
            <Box>
                <Typography variant="h6" color="textPrimary" sx={{ lineHeight: 1.2 }}>
                {CONFIG.CHAT_TITLE}
                </Typography>
                {/* Typing Indicator */}
                {typingStatus && (
                    <Typography variant="caption" sx={{ color: '#4caf50', fontStyle: 'italic', display: 'block' }}>
                        {typingStatus}
                    </Typography>
                )}
            </Box>
        </Box>
        <IconButton onClick={toggleDrawer(true)}>
            <MenuIcon />
        </IconButton>
      </Paper>

      {/* Drawer for Agents List */}
      <Drawer
        anchor="right"
        open={isDrawerOpen}
        onClose={toggleDrawer(false)}
      >
        {listAgents()}
      </Drawer>

      {/* Chat Area */}
      <Box sx={{ 
        flex: 1, 
        overflowY: 'auto', 
        p: 2, 
        bgcolor: '#ededed',
        display: 'flex',
        flexDirection: 'column',
        gap: 1
      }}>
        {messageHistory.map((msg, index) => (
          <Box 
            key={msg.id || index}
            sx={{ 
              display: 'flex', 
              justifyContent: msg.isUser ? 'flex-end' : 'flex-start',
              alignItems: 'flex-start',
              mb: 1
            }}
          >
            {!msg.isUser && (
              <Avatar 
                sx={{ 
                  bgcolor: CONFIG.AVATAR_COLORS[msg.sender] || CONFIG.DEFAULT_AVATAR_COLOR, 
                  width: 32, 
                  height: 32,
                  mr: 1,
                  fontSize: '14px'
                }}
              >
                {msg.sender[0]}
              </Avatar>
            )}
            
            <Box sx={{ maxWidth: '75%' }}>
              {!msg.isUser && (
                <Typography variant="caption" color="textSecondary" sx={{ ml: 1 }}>
                  {msg.sender}
                </Typography>
              )}
              <Paper 
                elevation={1} 
                sx={{ 
                  p: 1.5, 
                  bgcolor: msg.isUser ? '#95ec69' : '#fff',
                  borderRadius: 2,
                  wordBreak: 'break-word',
                  minWidth: '40px'
                }}
              >
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {msg.content}
                </Typography>
              </Paper>
            </Box>

            {msg.isUser && (
              <Avatar 
                sx={{ 
                  bgcolor: CONFIG.AVATAR_COLORS['你'], 
                  width: 32, 
                  height: 32,
                  ml: 1,
                  fontSize: '14px'
                }}
              >
                你
              </Avatar>
            )}
          </Box>
        ))}
        <div ref={bottomRef} />
      </Box>

      {/* Input Area */}
      <Paper elevation={3} sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="发消息..."
          size="small"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          sx={{ mr: 1, bgcolor: '#fff' }}
        />
        <IconButton 
          color="primary" 
          onClick={handleSendMessage} 
          disabled={readyState !== ReadyState.OPEN}
        >
          <SendIcon />
        </IconButton>
      </Paper>
    </Container>
  );
}

export default App;
