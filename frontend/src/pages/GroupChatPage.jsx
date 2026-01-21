import React, { useState, useEffect, useRef } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import {
  Box, Paper, TextField, IconButton, Typography,
  Avatar, Drawer, List, ListItem, ListItemAvatar, ListItemText, Divider, Chip
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import GroupIcon from '@mui/icons-material/Group';
import MenuIcon from '@mui/icons-material/Menu';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ElectricBoltIcon from '@mui/icons-material/ElectricBolt';
import { CONFIG } from '../config';

// 渐变头像颜色
const getAvatarGradient = (name) => {
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    'linear-gradient(135deg, #00c6fb 0%, #005bea 100%)',
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return gradients[Math.abs(hash) % gradients.length];
};

function GroupChatPage() {
  const [messageHistory, setMessageHistory] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [agents, setAgents] = useState([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [typingStatus, setTypingStatus] = useState('');
  const incomingBuffer = useRef({});
  const bottomRef = useRef(null);

  // 获取群成员列表
  useEffect(() => {
    fetch(`${CONFIG.API_BASE_URL}/chat/agents`)
      .then(res => res.json())
      .then(data => setAgents(data))
      .catch(err => console.error("获取群成员失败:", err));
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
        console.error("解析错误", e);
      }
    }
  }, [lastMessage]);

  // 滚动到底部（只在有消息时才滚动）
  useEffect(() => {
    if (messageHistory.length > 0) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
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
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
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
      sx={{
        width: 320,
        height: '100%',
        background: 'linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
      }}
      role="presentation"
      onClick={toggleDrawer(false)}
      onKeyDown={toggleDrawer(false)}
    >
      {/* 标题区域 */}
      <Box
        sx={{
          p: 3,
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
        }}
      >
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(102, 126, 234, 0.4)',
          }}
        >
          <GroupIcon sx={{ color: '#fff', fontSize: 20 }} />
        </Box>
        <Box>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              color: '#fff',
            }}
          >
            群成员
          </Typography>
          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
            共 {agents.length} 位成员
          </Typography>
        </Box>
      </Box>

      {/* 成员列表 */}
      <List sx={{ p: 2 }}>
        {agents.map((agent, index) => (
          <React.Fragment key={agent.id}>
            <ListItem
              alignItems="flex-start"
              sx={{
                borderRadius: '12px',
                mb: 1,
                transition: 'all 0.3s ease',
                '&:hover': {
                  background: 'rgba(102, 126, 234, 0.1)',
                },
              }}
            >
              <ListItemAvatar>
                <Avatar
                  sx={{
                    background: getAvatarGradient(agent.name),
                    width: 44,
                    height: 44,
                    fontWeight: 600,
                    boxShadow: '0 0 15px rgba(102, 126, 234, 0.3)',
                  }}
                >
                  {agent.name[0]}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Typography
                    variant="subtitle1"
                    sx={{ fontWeight: 600, color: '#fff' }}
                  >
                    {agent.name}
                  </Typography>
                }
                secondary={
                  <Box>
                    <Typography
                      variant="body2"
                      sx={{ color: 'rgba(255,255,255,0.7)', mb: 0.5 }}
                    >
                      {agent.occupation}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{ color: 'rgba(255,255,255,0.4)' }}
                    >
                      {agent.personality}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
            {index < agents.length - 1 && (
              <Divider
                sx={{
                  borderColor: 'rgba(255, 255, 255, 0.05)',
                  my: 0.5,
                }}
              />
            )}
          </React.Fragment>
        ))}
      </List>
    </Box>
  );

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: '-50%',
          left: '-50%',
          width: '200%',
          height: '200%',
          background: 'radial-gradient(circle at 30% 20%, rgba(102, 126, 234, 0.1) 0%, transparent 50%), radial-gradient(circle at 70% 80%, rgba(240, 147, 251, 0.08) 0%, transparent 50%)',
          animation: 'gradientShift 15s ease infinite',
          backgroundSize: '200% 200%',
          pointerEvents: 'none',
        },
      }}
    >
      {/* Header */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          flexShrink: 0,
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          zIndex: 10,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 40,
              height: 40,
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              boxShadow: '0 0 20px rgba(102, 126, 234, 0.4)',
              mr: 1.5,
            }}
          >
            <GroupIcon sx={{ color: '#fff', fontSize: 20 }} />
          </Box>
          <Box>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.8) 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                lineHeight: 1.2,
              }}
            >
              {CONFIG.CHAT_TITLE || '智能群聊'}
            </Typography>
            {typingStatus ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <ElectricBoltIcon sx={{ fontSize: 12, color: '#43e97b' }} />
                <Typography
                  variant="caption"
                  sx={{ color: '#43e97b', fontStyle: 'italic' }}
                >
                  {typingStatus}
                </Typography>
              </Box>
            ) : (
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                与 AI 群体智慧对话
              </Typography>
            )}
          </Box>
        </Box>
        <IconButton
          onClick={toggleDrawer(true)}
          sx={{
            color: 'rgba(255,255,255,0.7)',
            '&:hover': {
              background: 'rgba(102, 126, 234, 0.2)',
              color: '#fff',
            },
          }}
        >
          <MenuIcon />
        </IconButton>
      </Paper>

      {/* Drawer for Agents List */}
      <Drawer
        anchor="right"
        open={isDrawerOpen}
        onClose={toggleDrawer(false)}
        PaperProps={{
          sx: {
            background: 'transparent',
            boxShadow: '-10px 0 40px rgba(0, 0, 0, 0.5)',
          },
        }}
      >
        {listAgents()}
      </Drawer>

      {/* Chat Area */}
      <Box
        sx={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          position: 'relative',
          zIndex: 1,
        }}
      >
        {/* 欢迎信息 */}
        {messageHistory.length === 0 && (
          <Box
            sx={{
              textAlign: 'center',
              py: 8,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3,
                boxShadow: '0 0 40px rgba(102, 126, 234, 0.3)',
              }}
            >
              <AutoAwesomeIcon sx={{ fontSize: 36, color: '#667eea' }} />
            </Box>
            <Typography
              variant="h6"
              sx={{
                color: 'rgba(255,255,255,0.8)',
                mb: 1,
              }}
            >
              欢迎来到智能群聊
            </Typography>
            <Typography sx={{ color: 'rgba(255,255,255,0.5)', mb: 2 }}>
              与多位 AI 角色进行群体对话，获得多元视角
            </Typography>
            {agents.length > 0 && (
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
                {agents.slice(0, 5).map((agent) => (
                  <Chip
                    key={agent.id}
                    avatar={
                      <Avatar
                        sx={{
                          background: getAvatarGradient(agent.name),
                          width: 24,
                          height: 24,
                        }}
                      >
                        {agent.name[0]}
                      </Avatar>
                    }
                    label={agent.name}
                    size="small"
                    sx={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      color: 'rgba(255,255,255,0.8)',
                    }}
                  />
                ))}
                {agents.length > 5 && (
                  <Chip
                    label={`+${agents.length - 5}`}
                    size="small"
                    sx={{
                      background: 'rgba(102, 126, 234, 0.2)',
                      border: '1px solid rgba(102, 126, 234, 0.3)',
                      color: '#667eea',
                    }}
                  />
                )}
              </Box>
            )}
          </Box>
        )}

        {/* 消息列表 */}
        {messageHistory.map((msg, index) => (
          <Box
            key={msg.id || index}
            sx={{
              display: 'flex',
              justifyContent: msg.isUser ? 'flex-end' : 'flex-start',
              alignItems: 'flex-start',
              animation: 'fadeIn 0.3s ease',
              '@keyframes fadeIn': {
                from: { opacity: 0, transform: 'translateY(10px)' },
                to: { opacity: 1, transform: 'translateY(0)' },
              },
            }}
          >
            {!msg.isUser && (
              <Avatar
                sx={{
                  background: getAvatarGradient(msg.sender),
                  width: 36,
                  height: 36,
                  mr: 1.5,
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  boxShadow: '0 0 15px rgba(102, 126, 234, 0.3)',
                }}
              >
                {msg.sender[0]}
              </Avatar>
            )}

            <Box sx={{ maxWidth: '70%' }}>
              {!msg.isUser && (
                <Typography
                  variant="caption"
                  sx={{
                    color: 'rgba(255,255,255,0.5)',
                    ml: 1,
                    display: 'block',
                    mb: 0.5,
                  }}
                >
                  {msg.sender}
                </Typography>
              )}
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  background: msg.isUser
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : 'rgba(255, 255, 255, 0.08)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: msg.isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                  border: msg.isUser
                    ? 'none'
                    : '1px solid rgba(255, 255, 255, 0.1)',
                  boxShadow: msg.isUser
                    ? '0 4px 20px rgba(102, 126, 234, 0.4)'
                    : '0 4px 20px rgba(0, 0, 0, 0.2)',
                }}
              >
                <Typography
                  variant="body1"
                  sx={{
                    color: msg.isUser ? '#fff' : 'rgba(255,255,255,0.9)',
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.6,
                  }}
                >
                  {msg.content}
                </Typography>
              </Paper>
            </Box>

            {msg.isUser && (
              <Avatar
                sx={{
                  background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                  width: 36,
                  height: 36,
                  ml: 1.5,
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  boxShadow: '0 0 15px rgba(67, 233, 123, 0.3)',
                }}
              >
                你
              </Avatar>
            )}
          </Box>
        ))}

        {/* 打字指示器 */}
        {typingStatus && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                display: 'flex',
                gap: 0.5,
                p: 1.5,
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '12px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
              }}
            >
              {[0, 1, 2].map((i) => (
                <Box
                  key={i}
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    animation: `pulse 1.4s ${i * 0.2}s infinite ease-in-out`,
                    '@keyframes pulse': {
                      '0%, 80%, 100%': { transform: 'scale(0.6)', opacity: 0.5 },
                      '40%': { transform: 'scale(1)', opacity: 1 },
                    },
                  }}
                />
              ))}
            </Box>
          </Box>
        )}

        <div ref={bottomRef} />
      </Box>

      {/* Input Area */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          flexShrink: 0,
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          zIndex: 10,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="发送消息..."
            size="small"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            sx={{
              '& .MuiOutlinedInput-root': {
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '12px',
                color: '#fff',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(102, 126, 234, 0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#667eea',
                  boxShadow: '0 0 10px rgba(102, 126, 234, 0.3)',
                },
              },
              '& .MuiInputBase-input::placeholder': {
                color: 'rgba(255, 255, 255, 0.4)',
              },
            }}
          />
          <IconButton
            onClick={handleSendMessage}
            disabled={readyState !== ReadyState.OPEN || !inputMessage.trim()}
            sx={{
              width: 48,
              height: 48,
              background: inputMessage.trim()
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : 'rgba(255, 255, 255, 0.1)',
              boxShadow: inputMessage.trim()
                ? '0 0 20px rgba(102, 126, 234, 0.4)'
                : 'none',
              transition: 'all 0.3s ease',
              '&:hover': {
                background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                transform: 'scale(1.05)',
              },
              '&.Mui-disabled': {
                background: 'rgba(255, 255, 255, 0.05)',
              },
            }}
          >
            <SendIcon sx={{ color: '#fff' }} />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
}

export default GroupChatPage;
