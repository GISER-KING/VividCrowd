import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Container, Paper, TextField, IconButton, Typography,
  Avatar, Tabs, Tab, Divider, Dialog, DialogTitle, DialogContent,
  DialogActions, Button, Chip, InputAdornment
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ElectricBoltIcon from '@mui/icons-material/ElectricBolt';
import CelebritySelector from '../components/celebrity/CelebritySelector';
import CelebrityUpload from '../components/celebrity/CelebrityUpload';
import ChatModeToggle from '../components/celebrity/ChatModeToggle';
import useCelebrityWebSocket from '../hooks/useCelebrityWebSocket';
import { CONFIG } from '../config';

function CelebrityPage() {
  const [celebrities, setCelebrities] = useState([]);
  const [selectedCelebrities, setSelectedCelebrities] = useState([]);
  const [chatMode, setChatMode] = useState('private');
  const [inputMessage, setInputMessage] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const bottomRef = useRef(null);

  const {
    messages,
    sendMessage,
    clearMessages,
    typingStatus,
    isConnected,
  } = useCelebrityWebSocket(selectedCelebrities, chatMode);

  useEffect(() => {
    fetchCelebrities();
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, typingStatus]);

  useEffect(() => {
    if (chatMode === 'private' && selectedCelebrities.length > 1) {
      setSelectedCelebrities([selectedCelebrities[0]]);
    }
  }, [chatMode]);

  const fetchCelebrities = async () => {
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/celebrities`);
      if (response.ok) {
        const data = await response.json();
        setCelebrities(data);
      }
    } catch (err) {
      console.error('Failed to fetch celebrities:', err);
    }
  };

  const handleSendMessage = () => {
    if (inputMessage.trim() === '' || selectedCelebrities.length === 0) return;
    sendMessage(inputMessage);
    setInputMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      const response = await fetch(
        `${CONFIG.API_BASE_URL}/celebrities/${deleteTarget.id}`,
        { method: 'DELETE' }
      );
      if (response.ok) {
        setCelebrities((prev) => prev.filter((c) => c.id !== deleteTarget.id));
        setSelectedCelebrities((prev) =>
          prev.filter((c) => c.id !== deleteTarget.id)
        );
      }
    } catch (err) {
      console.error('Failed to delete celebrity:', err);
    }
    setDeleteTarget(null);
  };

  const handleUploadSuccess = (newCelebrity) => {
    setCelebrities((prev) => [...prev, newCelebrity]);
  };

  const getAvatarColor = (name) => {
    const colors = [
      'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
    ];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

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
          position: 'relative',
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          zIndex: 10,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
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
              <AutoAwesomeIcon sx={{ color: '#fff', fontSize: 20 }} />
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
                }}
              >
                数字分身
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                与商业巨擘对话，获取智慧洞见
              </Typography>
            </Box>
          </Box>
          <ChatModeToggle mode={chatMode} onChange={setChatMode} />
        </Box>
        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          sx={{
            minHeight: 44,
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: '12px',
            p: 0.5,
            '& .MuiTab-root': {
              minHeight: 36,
              borderRadius: '8px',
              color: 'rgba(255,255,255,0.6)',
              fontWeight: 600,
              fontSize: '0.9rem',
              transition: 'all 0.3s ease',
              '&.Mui-selected': {
                color: '#fff',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 0 15px rgba(102, 126, 234, 0.4)',
              },
              '&:hover:not(.Mui-selected)': {
                background: 'rgba(102, 126, 234, 0.1)',
                color: 'rgba(255,255,255,0.8)',
              },
            },
            '& .MuiTabs-indicator': {
              display: 'none',
            },
          }}
        >
          <Tab label="智能对话" />
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                智囊管理
                {celebrities.length === 0 && (
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: '#f093fb',
                      animation: 'pulse 2s infinite',
                      '@keyframes pulse': {
                        '0%, 100%': { opacity: 1, transform: 'scale(1)' },
                        '50%': { opacity: 0.5, transform: 'scale(0.8)' },
                      },
                    }}
                  />
                )}
              </Box>
            }
          />
        </Tabs>
      </Paper>

      {/* Main Content */}
      <Box sx={{ flex: 1, minHeight: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 1 }}>
        {activeTab === 0 ? (
          <>
            {/* 名人选择区域 */}
            <Box
              sx={{
                p: 2,
                flexShrink: 0,
                background: 'rgba(255, 255, 255, 0.02)',
                borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
              }}
            >
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 1.5 }}>
                {chatMode === 'private' ? '选择一位智者进行深度对话' : '组建你的专属智囊团'}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
                {celebrities.map((c) => {
                  const isSelected = selectedCelebrities.some((s) => s.id === c.id);
                  return (
                    <Box
                      key={c.id}
                      onClick={() => {
                        if (chatMode === 'private') {
                          setSelectedCelebrities(isSelected ? [] : [c]);
                        } else {
                          setSelectedCelebrities((prev) =>
                            isSelected
                              ? prev.filter((s) => s.id !== c.id)
                              : [...prev, c]
                          );
                        }
                      }}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        px: 2,
                        py: 1,
                        borderRadius: '20px',
                        cursor: 'pointer',
                        background: isSelected
                          ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%)'
                          : 'rgba(255, 255, 255, 0.05)',
                        border: isSelected
                          ? '1px solid rgba(102, 126, 234, 0.6)'
                          : '1px solid rgba(255, 255, 255, 0.1)',
                        boxShadow: isSelected
                          ? '0 0 20px rgba(102, 126, 234, 0.3)'
                          : 'none',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                          border: '1px solid rgba(102, 126, 234, 0.4)',
                          transform: 'translateY(-2px)',
                        },
                      }}
                    >
                      <Avatar
                        sx={{
                          width: 28,
                          height: 28,
                          fontSize: '0.85rem',
                          fontWeight: 600,
                          background: getAvatarColor(c.name),
                          boxShadow: isSelected ? '0 0 10px rgba(102, 126, 234, 0.5)' : 'none',
                        }}
                      >
                        {c.name[0]}
                      </Avatar>
                      <Typography
                        variant="body2"
                        sx={{
                          color: isSelected ? '#fff' : 'rgba(255,255,255,0.8)',
                          fontWeight: isSelected ? 600 : 400,
                        }}
                      >
                        {c.name}
                      </Typography>
                      {isSelected && (
                        <ElectricBoltIcon sx={{ fontSize: 14, color: '#f093fb' }} />
                      )}
                    </Box>
                  );
                })}
                {celebrities.length === 0 && (
                  <Box
                    onClick={() => setActiveTab(1)}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                      p: 2,
                      borderRadius: '16px',
                      background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
                      border: '1px dashed rgba(102, 126, 234, 0.4)',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                        border: '1px dashed rgba(102, 126, 234, 0.6)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 20px rgba(102, 126, 234, 0.2)',
                      },
                    }}
                  >
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <AutoAwesomeIcon sx={{ fontSize: 20, color: '#667eea' }} />
                    </Box>
                    <Box>
                      <Typography variant="body2" sx={{ color: '#fff', fontWeight: 600 }}>
                        暂无智囊数据
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                        点击此处前往「智囊管理」上传 PDF 文件
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Box>
            </Box>

            {/* 聊天区域 */}
            <Box
              sx={{
                flex: 1,
                minHeight: 0,
                overflowY: 'auto',
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
              }}
            >
              {messages.length === 0 && selectedCelebrities.length > 0 && (
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
                    准备就绪
                  </Typography>
                  <Typography sx={{ color: 'rgba(255,255,255,0.5)' }}>
                    与 {selectedCelebrities.map((c) => c.name).join('、')} 开启智慧对话
                  </Typography>
                </Box>
              )}

              {messages.length === 0 && selectedCelebrities.length === 0 && (
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
                      width: 100,
                      height: 100,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 3,
                      boxShadow: '0 0 60px rgba(102, 126, 234, 0.2)',
                      animation: 'float 6s ease-in-out infinite',
                      '@keyframes float': {
                        '0%, 100%': { transform: 'translateY(0)' },
                        '50%': { transform: 'translateY(-10px)' },
                      },
                    }}
                  >
                    <AutoAwesomeIcon sx={{ fontSize: 48, color: '#667eea' }} />
                  </Box>
                  <Typography
                    variant="h6"
                    sx={{
                      color: 'rgba(255,255,255,0.7)',
                      mb: 1,
                      fontWeight: 600,
                    }}
                  >
                    {celebrities.length === 0 ? '开始你的智囊之旅' : '请选择一位智者'}
                  </Typography>
                  <Typography sx={{ color: 'rgba(255,255,255,0.4)', mb: 3, maxWidth: 300 }}>
                    {celebrities.length === 0
                      ? '上传商业巨擘的著作、课程或信件，AI 将学习并模拟其思维方式'
                      : '从上方选择一位或多位智者，开启智慧对话'
                    }
                  </Typography>
                  {celebrities.length === 0 && (
                    <Button
                      onClick={() => setActiveTab(1)}
                      variant="contained"
                      startIcon={<AutoAwesomeIcon />}
                      sx={{
                        px: 4,
                        py: 1.5,
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        boxShadow: '0 0 20px rgba(102, 126, 234, 0.4)',
                        fontWeight: 600,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                          boxShadow: '0 0 30px rgba(102, 126, 234, 0.6)',
                          transform: 'translateY(-2px)',
                        },
                      }}
                    >
                      前往智囊管理
                    </Button>
                  )}
                </Box>
              )}

              {messages.map((msg) => (
                <Box
                  key={msg.id}
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
                        background: msg.isError
                          ? 'linear-gradient(135deg, #666 0%, #444 100%)'
                          : getAvatarColor(msg.sender),
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
                          : msg.isError
                          ? 'rgba(244, 67, 54, 0.1)'
                          : 'rgba(255, 255, 255, 0.08)',
                        backdropFilter: 'blur(10px)',
                        borderRadius: msg.isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                        border: msg.isUser
                          ? 'none'
                          : msg.isError
                          ? '1px solid rgba(244, 67, 54, 0.3)'
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
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                    {typingStatus}
                  </Typography>
                </Box>
              )}

              <div ref={bottomRef} />
            </Box>

            {/* 输入区域 */}
            <Paper
              elevation={0}
              sx={{
                p: 2,
                flexShrink: 0,
                background: 'rgba(255, 255, 255, 0.03)',
                backdropFilter: 'blur(20px)',
                borderTop: '1px solid rgba(255, 255, 255, 0.08)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder={
                    selectedCelebrities.length === 0
                      ? '请先选择智者...'
                      : `向 ${selectedCelebrities.map((c) => c.name).join('、')} 提问...`
                  }
                  size="small"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={selectedCelebrities.length === 0}
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
                  disabled={!isConnected || selectedCelebrities.length === 0 || !inputMessage.trim()}
                  sx={{
                    width: 48,
                    height: 48,
                    background: inputMessage.trim() && selectedCelebrities.length > 0
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : 'rgba(255, 255, 255, 0.1)',
                    boxShadow: inputMessage.trim() && selectedCelebrities.length > 0
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
          </>
        ) : (
          // 名人管理页面
          <Box sx={{ flex: 1, minHeight: 0, overflowY: 'auto', p: 3 }}>
            <Box sx={{ mb: 4 }}>
              <CelebrityUpload onUploadSuccess={handleUploadSuccess} />
            </Box>
            <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', my: 3 }} />
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  color: '#fff',
                  fontWeight: 600,
                }}
              >
                智囊团成员
              </Typography>
              <Chip
                label={celebrities.length}
                size="small"
                sx={{
                  ml: 1.5,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: '#fff',
                  fontWeight: 600,
                }}
              />
            </Box>
            <CelebritySelector
              celebrities={celebrities}
              selectedCelebrities={selectedCelebrities}
              onSelect={setSelectedCelebrities}
              onDelete={(c) => setDeleteTarget(c)}
              chatMode={chatMode}
            />
          </Box>
        )}
      </Box>

      {/* 删除确认对话框 */}
      <Dialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
          },
        }}
      >
        <DialogTitle sx={{ color: '#fff' }}>确认删除</DialogTitle>
        <DialogContent>
          <Typography sx={{ color: 'rgba(255,255,255,0.8)' }}>
            确定要删除 "{deleteTarget?.name}" 吗？此操作不可恢复。
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button
            onClick={() => setDeleteTarget(null)}
            sx={{ color: 'rgba(255,255,255,0.6)' }}
          >
            取消
          </Button>
          <Button
            onClick={handleDelete}
            sx={{
              background: 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)',
              color: '#fff',
              '&:hover': {
                background: 'linear-gradient(135deg, #d32f2f 0%, #f44336 100%)',
              },
            }}
          >
            删除
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default CelebrityPage;
