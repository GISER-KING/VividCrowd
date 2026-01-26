import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Paper, TextField, IconButton, Typography, Avatar, Tabs, Tab,
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Chip, List,
  ListItem, ListItemButton, ListItemText, ListItemAvatar, Grid
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import DeleteIcon from '@mui/icons-material/Delete';
import DigitalCustomerUpload from '../components/digital_customer/DigitalCustomerUpload';
import { CONFIG } from '../config';

function DigitalCustomerPage() {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [typingStatus, setTypingStatus] = useState('');
  const chatContainerRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    fetchCustomers();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (messages.length > 0 && chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, typingStatus]);

  const fetchCustomers = async () => {
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/digital-customer`);
      if (response.ok) {
        const data = await response.json();
        setCustomers(data);
      }
    } catch (err) {
      console.error('Failed to fetch customers:', err);
    }
  };

  const connectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(CONFIG.DIGITAL_CUSTOMER_WS_URL);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('Digital Customer WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'stream_start') {
        setTypingStatus(`${data.sender} 正在输入...`);
      } else if (data.type === 'stream_chunk') {
        setMessages(prev => {
          // 非流式模式下，chunk 包含完整回复
          // 如果上一条是正在输入的消息（isStreaming=true），则替换它
          const lastMsg = prev[prev.length - 1];
          if (lastMsg && lastMsg.sender === data.sender && lastMsg.isStreaming) {
            return [...prev.slice(0, -1), {
              ...lastMsg,
              content: data.content // 直接替换为完整内容
            }];
          } else {
            return [...prev, {
              sender: data.sender,
              content: data.content,
              isUser: false,
              isStreaming: true
            }];
          }
        });
      } else if (data.type === 'stream_end') {
        setTypingStatus('');
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg && lastMsg.isStreaming) {
            return [...prev.slice(0, -1), { ...lastMsg, isStreaming: false }];
          }
          return prev;
        });
      } else if (data.type === 'error') {
        setTypingStatus('');
        setMessages(prev => [...prev, {
          sender: 'System',
          content: data.content,
          isUser: false,
          isError: true
        }]);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Digital Customer WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    wsRef.current = ws;
  };

  const handleCustomerSelect = (customer) => {
    setSelectedCustomer(customer);
    setMessages([]);
    setTypingStatus('');
    connectWebSocket();
  };

  const handleSendMessage = () => {
    if (inputMessage.trim() === '' || !selectedCustomer) return;

    if (!isConnected) {
      connectWebSocket();
      return;
    }

    const userMessage = {
      sender: '销售人员',
      content: inputMessage,
      isUser: true
    };
    setMessages(prev => [...prev, userMessage]);

    wsRef.current.send(JSON.stringify({
      message: inputMessage,
      customer_ids: [selectedCustomer.id],
      mode: 'private'
    }));

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
        `${CONFIG.API_BASE_URL}/digital-customer/${deleteTarget.id}`,
        { method: 'DELETE' }
      );
      if (response.ok) {
        setCustomers(prev => prev.filter(c => c.id !== deleteTarget.id));
        if (selectedCustomer?.id === deleteTarget.id) {
          setSelectedCustomer(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error('Failed to delete customer:', err);
    }
    setDeleteTarget(null);
  };

  const handleUploadSuccess = (newCustomer) => {
    setCustomers(prev => [...prev, newCustomer]);
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
      }}
    >
      {/* Header - Fixed */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          flexShrink: 0,
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          zIndex: 10,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <PersonIcon sx={{ color: '#fff', fontSize: 24 }} />
            </Box>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700, color: '#fff' }}>
                数字客户
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                销售能力培训系统
              </Typography>
            </Box>
          </Box>
          {selectedCustomer && (
            <Chip
              label={`当前客户: ${selectedCustomer.name}`}
              sx={{
                background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                color: '#fff',
                fontWeight: 600,
              }}
            />
          )}
        </Box>

        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          sx={{
            minHeight: 40,
            '& .MuiTab-root': {
              color: 'rgba(255,255,255,0.5)',
              minHeight: 40,
              '&.Mui-selected': { color: '#fff' },
            },
            '& .MuiTabs-indicator': {
              background: 'linear-gradient(90deg, #667eea, #764ba2)',
            },
          }}
        >
          <Tab label="对话训练" />
          <Tab label="客户管理" />
        </Tabs>
      </Paper>

      {/* Content Area - Scrollable */}
      <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex' }}>
        {activeTab === 0 ? (
          <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
            {/* Customer List */}
            <Paper
              elevation={0}
              sx={{
                width: 280,
                flexShrink: 0,
                background: 'rgba(255, 255, 255, 0.02)',
                borderRight: '1px solid rgba(255, 255, 255, 0.08)',
                overflow: 'auto',
              }}
            >
              <Box sx={{ p: 2 }}>
                <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 1 }}>
                  选择客户
                </Typography>
                <List>
                  {customers.map((customer) => (
                    <ListItem key={customer.id} disablePadding sx={{ mb: 1 }}>
                      <ListItemButton
                        selected={selectedCustomer?.id === customer.id}
                        onClick={() => handleCustomerSelect(customer)}
                        sx={{
                          borderRadius: '12px',
                          '&.Mui-selected': {
                            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%)',
                            border: '1px solid rgba(102, 126, 234, 0.5)',
                          },
                        }}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                            <PersonIcon />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={customer.name}
                          secondary={customer.occupation || '客户'}
                          primaryTypographyProps={{ sx: { color: '#fff', fontWeight: 600 } }}
                          secondaryTypographyProps={{ sx: { color: 'rgba(255,255,255,0.5)' } }}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Paper>

            {/* Chat Area */}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              {selectedCustomer ? (
                <>
                  {/* Messages - Scrollable */}
                  <Box
                    ref={chatContainerRef}
                    sx={{
                      flex: 1,
                      overflow: 'auto',
                      p: 3,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 2,
                    }}
                  >
                    {messages.map((msg, idx) => (
                      <Box
                        key={idx}
                        sx={{
                          display: 'flex',
                          justifyContent: msg.isUser ? 'flex-end' : 'flex-start',
                        }}
                      >
                        <Paper
                          sx={{
                            p: 2,
                            maxWidth: '70%',
                            background: msg.isUser
                              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                              : msg.isError
                              ? 'rgba(244, 67, 54, 0.2)'
                              : 'rgba(255, 255, 255, 0.05)',
                            color: '#fff',
                            borderRadius: '16px',
                          }}
                        >
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', mb: 0.5, display: 'block' }}>
                            {msg.sender}
                          </Typography>
                          <Typography sx={{ whiteSpace: 'pre-wrap' }}>{msg.content}</Typography>
                        </Paper>
                      </Box>
                    ))}
                    {typingStatus && (
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', ml: 2 }}>
                        {typingStatus}
                      </Typography>
                    )}
                  </Box>
                </>
              ) : (
                <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography sx={{ color: 'rgba(255,255,255,0.5)' }}>
                    请从左侧选择一个客户开始对话训练
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        ) : (
          <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <DigitalCustomerUpload onUploadSuccess={handleUploadSuccess} />
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper
                  sx={{
                    p: 3,
                    background: 'rgba(255, 255, 255, 0.03)',
                    backdropFilter: 'blur(20px)',
                    borderRadius: '20px',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                  }}
                >
                  <Typography variant="h6" sx={{ color: '#fff', mb: 2, fontWeight: 700 }}>
                    客户列表
                  </Typography>
                  <List>
                    {customers.map((customer) => (
                      <ListItem
                        key={customer.id}
                        secondaryAction={
                          <IconButton
                            edge="end"
                            onClick={() => setDeleteTarget(customer)}
                            sx={{ color: 'rgba(244, 67, 54, 0.8)' }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        }
                        sx={{
                          mb: 1,
                          background: 'rgba(255, 255, 255, 0.05)',
                          borderRadius: '12px',
                        }}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                            <PersonIcon />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={customer.name}
                          secondary={`${customer.occupation || ''} | ${customer.industry || ''}`}
                          primaryTypographyProps={{ sx: { color: '#fff', fontWeight: 600 } }}
                          secondaryTypographyProps={{ sx: { color: 'rgba(255,255,255,0.5)' } }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>

      {/* Input Area - Fixed */}
      {activeTab === 0 && selectedCustomer && (
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
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isConnected ? "输入您的销售话术..." : "正在连接..."}
              sx={{
                '& .MuiOutlinedInput-root': {
                  background: 'rgba(255, 255, 255, 0.05)',
                  color: '#fff',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.1)' },
                  '&:hover fieldset': { borderColor: 'rgba(102, 126, 234, 0.5)' },
                  '&.Mui-focused fieldset': { borderColor: '#667eea' },
                },
              }}
            />
            <IconButton
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || !isConnected}
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: '#fff',
                '&:hover': { background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)' },
                '&.Mui-disabled': { background: 'rgba(255, 255, 255, 0.1)', color: 'rgba(255, 255, 255, 0.3)' },
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)}>
        <DialogTitle>确认删除</DialogTitle>
        <DialogContent>
          确定要删除客户画像 "{deleteTarget?.name}" 吗？
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteTarget(null)}>取消</Button>
          <Button onClick={handleDelete} color="error">删除</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default DigitalCustomerPage;
