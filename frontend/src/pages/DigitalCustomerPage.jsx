import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Paper, TextField, IconButton, Typography, Avatar, Tabs, Tab,
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Chip, List,
  ListItem, ListItemButton, ListItemText, ListItemAvatar, Grid, Snackbar, Alert
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import DeleteIcon from '@mui/icons-material/Delete';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import SchoolIcon from '@mui/icons-material/School';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import { useNavigate } from 'react-router-dom';
import DigitalCustomerUpload from '../components/digital_customer/DigitalCustomerUpload';
import AudioInput from '../components/common/AudioInput';
import StageIndicator from '../components/training/StageIndicator';
import RealTimeFeedback from '../components/training/RealTimeFeedback';
import SalesCopilot from '../components/training/SalesCopilot';
import { CONFIG } from '../config';

function DigitalCustomerPage() {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0); // 0: 客户管理, 1: 培训记录
  const [trainingRecords, setTrainingRecords] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [typingStatus, setTypingStatus] = useState('');
  const [trainingDialog, setTrainingDialog] = useState(false);
  const [traineeName, setTraineeName] = useState('');

  // Training mode states
  const [trainingMode, setTrainingMode] = useState(false);
  const [trainingSessionId, setTrainingSessionId] = useState(null);
  const [currentStage, setCurrentStage] = useState(1);
  const [currentRound, setCurrentRound] = useState(0);
  const [completedStages, setCompletedStages] = useState([]);
  const [realtimeAnalysis, setRealtimeAnalysis] = useState(null);
  const [stageEvaluation, setStageEvaluation] = useState(null);
  const [trainingComplete, setTrainingComplete] = useState(false);
  const [finalEvaluation, setFinalEvaluation] = useState(null);

  const chatContainerRef = useRef(null);
  const wsRef = useRef(null);
  const currentResponseRef = useRef('');
  const audioRef = useRef(null);

  useEffect(() => {
    fetchCustomers();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      stopAudio();
    };
  }, []);

  useEffect(() => {
    if (messages.length > 0 && chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, typingStatus]);

  useEffect(() => {
    if (activeTab === 1) {
      fetchTrainingRecords();
    }
  }, [activeTab]);

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

  const fetchTrainingRecords = async () => {
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/digital-customer/training/sessions`);
      if (response.ok) {
        const data = await response.json();
        setTrainingRecords(data.records || []);
      }
    } catch (err) {
      console.error('Failed to fetch training records:', err);
    }
  };

  const handleNormalMessage = (data) => {
    // 普通模式已移除，此函数保留以防万一
    console.warn('Normal message received but normal mode is disabled');
  };

  const handleTrainingMessage = (data) => {
    switch (data.type) {
      case 'analysis':
        // 实时分析反馈
        setRealtimeAnalysis({
          quality: data.quality,
          issues: data.issues || [],
          suggestions: data.suggestions || []
        });
        setCurrentStage(data.stage);
        setCurrentRound(data.round);
        break;

      case 'stream_start':
        // 客户开始回复 - 初始化缓冲区
        currentResponseRef.current = '';
        setMessages(prev => [...prev, {
          sender: selectedCustomer.name,
          content: '正在思考...',
          isUser: false,
          isStreaming: true,
          isThinking: true
        }]);
        break;

      case 'stream_chunk':
        // 流式内容 - 累积文本但不立即显示
        currentResponseRef.current += data.content;
        break;

      case 'stream_end':
        // 流式结束 - 生成音频并同步显示文字
        const fullText = currentResponseRef.current;
        
        // 播放音频，成功开始播放后显示文字
        playAudio(fullText).then(() => {
          setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.isStreaming) {
              return [...prev.slice(0, -1), { 
                ...lastMsg, 
                content: fullText, 
                isStreaming: false,
                isThinking: false
              }];
            }
            return prev;
          });
        }).catch(err => {
          console.error("Audio playback failed:", err);
          // 音频播放失败也要显示文字
          setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.isStreaming) {
              return [...prev.slice(0, -1), { 
                ...lastMsg, 
                content: fullText, 
                isStreaming: false,
                isThinking: false
              }];
            }
            return prev;
          });
        });
        break;

      case 'stage_complete':
        // 阶段完成
        setStageEvaluation({
          stage: data.stage,
          score: data.score,
          feedback: data.feedback
        });
        setCompletedStages(prev => [...prev, data.stage]);
        break;

      case 'training_complete':
        // 培训完成
        setStageEvaluation(null);  // 关闭阶段评价对话框，避免窗口重叠
        setTrainingComplete(true);
        setFinalEvaluation(data.evaluation);
        break;

      case 'error':
        // 错误消息
        setMessages(prev => [...prev, {
          sender: 'System',
          content: data.content,
          isUser: false,
          isError: true
        }]);
        break;

      default:
        break;
    }
  };

  const connectWebSocket = (isTraining = false, sessionId = null) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    // 只支持培训模式的 WebSocket 连接
    if (!isTraining || !sessionId) {
      console.error('WebSocket connection requires training mode and session ID');
      return;
    }

    const wsUrl = `${CONFIG.TRAINING_WS_URL}/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('Training WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleTrainingMessage(data);
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    wsRef.current = ws;
  };

  const handleCustomerSelect = (customer) => {
    setSelectedCustomer(customer);
    // 客户选择后不再自动连接，只在开始培训时连接
  };

  const handleSendMessage = () => {
    if (inputMessage.trim() === '' || !selectedCustomer) return;

    if (!isConnected) {
      connectWebSocket(true, trainingSessionId);
      return;
    }

    const userMessage = {
      sender: '销售人员',
      content: inputMessage,
      isUser: true
    };
    setMessages(prev => [...prev, userMessage]);

    // 培训模式：只发送消息内容
    wsRef.current.send(JSON.stringify({
      message: inputMessage
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
        // 删除成功，更新本地状态
        setCustomers(prev => prev.filter(c => c.id !== deleteTarget.id));
        if (selectedCustomer?.id === deleteTarget.id) {
          setSelectedCustomer(null);
          setMessages([]);
        }
        setDeleteTarget(null);  // 只在成功时关闭对话框
      } else {
        // 删除失败，显示错误信息
        const errorData = await response.json().catch(() => ({ detail: '删除失败' }));
        setError(errorData.detail || '删除客户失败，请重试');
      }
    } catch (err) {
      console.error('Failed to delete customer:', err);
      setError('网络错误，无法删除客户');
    }
  };

  const handleUploadSuccess = (newCustomer) => {
    setCustomers(prev => [...prev, newCustomer]);
  };

  const handleStartTraining = () => {
    if (!selectedCustomer) {
      alert('请先选择一个客户');
      return;
    }
    setTrainingDialog(true);
  };

  const handleTrainingConfirm = async () => {
    if (!traineeName.trim()) {
      alert('请输入您的姓名');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('trainee_id', Date.now().toString());
      formData.append('trainee_name', traineeName);
      formData.append('customer_id', selectedCustomer.id);

      const response = await fetch(
        `${CONFIG.API_BASE_URL}/digital-customer/training/sessions/start`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (response.ok) {
        const data = await response.json();

        // 进入培训模式
        setTrainingMode(true);
        setTrainingSessionId(data.session_id);
        setCurrentStage(1);
        setCurrentRound(0);
        setCompletedStages([]);
        setRealtimeAnalysis(null);
        setStageEvaluation(null);
        setTrainingComplete(false);
        setFinalEvaluation(null);
        setMessages([]);  // 清空消息

        // 关闭对话框
        setTrainingDialog(false);
        setTraineeName('');

        // 连接培训 WebSocket
        connectWebSocket(true, data.session_id);
      } else {
        alert('启动培训失败');
      }
    } catch (err) {
      console.error('Failed to start training:', err);
      alert('启动培训失败');
    }
  };

  const handleExitTraining = () => {
    // 确认退出
    if (!window.confirm('确定要退出培训吗？培训进度将不会保存。')) {
      return;
    }

    // 重置培训状态
    setTrainingMode(false);
    setTrainingSessionId(null);
    setCurrentStage(1);
    setCurrentRound(0);
    setCompletedStages([]);
    setRealtimeAnalysis(null);
    setStageEvaluation(null);
    setTrainingComplete(false);
    setFinalEvaluation(null);
    setMessages([]);

    // 关闭 WebSocket 连接
    if (wsRef.current) {
      wsRef.current.close();
    }
    setIsConnected(false);
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
  };

  const playAudio = async (text) => {
    if (!text) return;

    // 停止当前正在播放的音频
    stopAudio();

    try {
        const formData = new FormData();
        formData.append('text', text);
        formData.append('voice', 'longxiaochun');

        const response = await fetch(`${CONFIG.API_BASE_URL}/digital-customer/audio/synthesize`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const audio = new Audio(URL.createObjectURL(blob));
            audioRef.current = audio;  // 保存引用

            // 播放结束后清理引用
            audio.onended = () => {
              audioRef.current = null;
            };

            // 错误处理
            audio.onerror = () => {
              console.error("Audio playback error");
              audioRef.current = null;
            };

            await audio.play();
        }
    } catch (err) {
        console.error("TTS failed", err);
        audioRef.current = null;
    }
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
          <Box sx={{ display: 'flex', gap: 1 }}>
            {selectedCustomer && (
              <Chip
                label={`当前客户: ${selectedCustomer.name || selectedCustomer.profile_type}`}
                sx={{
                  background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                  color: '#fff',
                  fontWeight: 600,
                }}
              />
            )}
            {trainingMode ? (
              <Button
                startIcon={<ExitToAppIcon />}
                onClick={handleExitTraining}
                variant="contained"
                size="small"
                sx={{
                  background: 'linear-gradient(135deg, #f44336 0%, #e91e63 100%)',
                  color: '#fff',
                  fontWeight: 600,
                  '&:hover': {
                    background: 'linear-gradient(135deg, #e91e63 0%, #f44336 100%)',
                  },
                }}
              >
                退出培训
              </Button>
            ) : (
              <Button
                startIcon={<SchoolIcon />}
                onClick={handleStartTraining}
                variant="contained"
                size="small"
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: '#fff',
                  fontWeight: 600,
                  '&:hover': {
                    background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                  },
                }}
              >
                开始培训
              </Button>
            )}
          </Box>
        </Box>

        {trainingMode ? (
          <StageIndicator currentStage={currentStage} completedStages={completedStages} />
        ) : null}
      </Paper>

      {/* Content Area - Scrollable */}
      <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex' }}>
        {trainingMode ? (
          <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
            
            {/* Sales Copilot - Left Side */}
            <Box
              sx={{
                width: 350, // Slightly wider for chat
                flexShrink: 0,
                overflow: 'hidden', // Copilot handles its own scroll
                p: 2,
                background: 'rgba(255, 255, 255, 0.02)',
                borderRight: '1px solid rgba(255, 255, 255, 0.08)',
                display: { xs: 'none', md: 'block' } // Hide on small screens
              }}
            >
              <SalesCopilot
                currentStage={currentStage}
                suggestions={realtimeAnalysis?.suggestions || []}
                onUseSuggestion={(text) => setInputMessage(text)}
                customerId={selectedCustomer?.id}
                sessionId={trainingSessionId}
              />
            </Box>

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
                          {/* 播放按钮 */}
                          {msg.sender !== '销售人员' && !msg.isUser && !msg.isError && (
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 0.5 }}>
                                <IconButton
                                    size="small"
                                    onClick={() => playAudio(msg.content)}
                                    sx={{ color: 'rgba(255,255,255,0.7)', '&:hover': { color: '#fff' } }}
                                    title="播放语音"
                                >
                                    <VolumeUpIcon fontSize="small" />
                                </IconButton>
                            </Box>
                          )}
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
                    培训会话加载中...
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Real-time Feedback Panel - Only in training mode */}
            <Box
              sx={{
                width: 360,
                flexShrink: 0,
                overflow: 'auto',
                p: 2,
                background: 'rgba(255, 255, 255, 0.02)',
                borderLeft: '1px solid rgba(255, 255, 255, 0.08)',
              }}
            >
              <RealTimeFeedback
                analysis={realtimeAnalysis}
                currentStage={currentStage}
                currentRound={currentRound}
              />
            </Box>
          </Box>
        ) : (
          <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
            {/* Tab 切换 */}
            <Box sx={{ borderBottom: 1, borderColor: 'rgba(255, 255, 255, 0.1)', mb: 3 }}>
              <Tabs
                value={activeTab}
                onChange={(e, newValue) => setActiveTab(newValue)}
                sx={{
                  '& .MuiTab-root': {
                    color: 'rgba(255, 255, 255, 0.6)',
                    fontWeight: 600,
                  },
                  '& .Mui-selected': {
                    color: '#43e97b',
                  },
                  '& .MuiTabs-indicator': {
                    backgroundColor: '#43e97b',
                  },
                }}
              >
                <Tab label="客户管理" />
                <Tab label="培训记录" />
              </Tabs>
            </Box>

            {/* 客户管理 Tab */}
            {activeTab === 0 && (
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
                          background: selectedCustomer?.id === customer.id
                            ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%)'
                            : 'rgba(255, 255, 255, 0.05)',
                          borderRadius: '12px',
                          border: selectedCustomer?.id === customer.id
                            ? '1px solid rgba(102, 126, 234, 0.5)'
                            : '1px solid transparent',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            background: selectedCustomer?.id === customer.id
                              ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.4) 0%, rgba(118, 75, 162, 0.4) 100%)'
                              : 'rgba(255, 255, 255, 0.08)',
                          },
                        }}
                        onClick={() => setSelectedCustomer(customer)}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                            <PersonIcon />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={customer.name || customer.profile_type}
                          secondary={
                            customer.name
                              ? `${customer.profile_type} | ${customer.occupation || ''} | ${customer.industry || ''}`
                              : `${customer.occupation || ''} | ${customer.industry || ''}`
                          }
                          primaryTypographyProps={{ sx: { color: '#fff', fontWeight: 600 } }}
                          secondaryTypographyProps={{ sx: { color: 'rgba(255,255,255,0.5)' } }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Grid>
            </Grid>
            )}

            {/* 培训记录 Tab */}
            {activeTab === 1 && (
              <Paper
                sx={{
                  p: 3,
                  background: 'rgba(255, 255, 255, 0.03)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '20px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                }}
              >
                <Typography variant="h6" sx={{ color: '#fff', mb: 3, fontWeight: 700 }}>
                  培训记录
                </Typography>
                {trainingRecords.length === 0 ? (
                  <Typography sx={{ color: 'rgba(255, 255, 255, 0.5)', textAlign: 'center', py: 4 }}>
                    暂无培训记录
                  </Typography>
                ) : (
                  <List>
                    {trainingRecords.map((record) => (
                      <ListItem
                        key={record.id}
                        onClick={() => navigate(`/training/evaluation?session_id=${record.session_id}`)}
                        sx={{
                          mb: 2,
                          background: 'rgba(255, 255, 255, 0.05)',
                          borderRadius: '12px',
                          border: '1px solid rgba(255, 255, 255, 0.08)',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            background: 'rgba(255, 255, 255, 0.08)',
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 12px rgba(67, 233, 123, 0.2)',
                          },
                        }}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                            <SchoolIcon />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography sx={{ color: '#fff', fontWeight: 600 }}>
                                {record.trainee_name}
                              </Typography>
                              <Typography sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                                vs
                              </Typography>
                              <Typography sx={{ color: '#43e97b', fontWeight: 600 }}>
                                {record.customer_name}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Box sx={{ mt: 1 }}>
                              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                                客户类型: {record.customer_profile_type} |
                                阶段: {record.current_stage} |
                                轮次: {record.total_rounds} |
                                状态: {record.status === 'active' ? '进行中' : '已完成'}
                              </Typography>
                              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.3)', mt: 0.5, display: 'block' }}>
                                {new Date(record.created_at).toLocaleString('zh-CN')}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </Paper>
            )}
          </Box>
        )}
      </Box>

      {/* Input Area - Fixed - Only in training mode */}
      {trainingMode && selectedCustomer && (
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
            <AudioInput onTextRecognized={(text) => setInputMessage(prev => prev + text)} />
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

      {/* Training Start Dialog */}
      <Dialog
        open={trainingDialog}
        onClose={() => setTrainingDialog(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'rgba(26, 26, 46, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '20px',
          },
        }}
      >
        <DialogTitle sx={{ color: '#fff', textAlign: 'center' }}>
          <SchoolIcon sx={{ fontSize: 48, color: '#667eea', mb: 1 }} />
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            开始销售培训
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 3, textAlign: 'center' }}>
            您将与 <strong style={{ color: '#43e97b' }}>
              {selectedCustomer?.name || selectedCustomer?.profile_type}
            </strong>
            {selectedCustomer?.name && selectedCustomer?.profile_type && (
              <span> ({selectedCustomer.profile_type})</span>
            )}
            进行销售培训对话
          </Typography>
          <TextField
            fullWidth
            label="您的姓名"
            value={traineeName}
            onChange={(e) => setTraineeName(e.target.value)}
            placeholder="请输入您的姓名"
            sx={{
              '& .MuiOutlinedInput-root': {
                background: 'rgba(255, 255, 255, 0.05)',
                color: '#fff',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                '&:hover fieldset': { borderColor: 'rgba(102, 126, 234, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: '#667eea' },
              },
              '& .MuiInputLabel-root': {
                color: 'rgba(255, 255, 255, 0.7)',
                '&.Mui-focused': { color: '#667eea' },
              },
            }}
          />
          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', mt: 2, display: 'block' }}>
            培训将包含5个阶段，系统会实时评价您的销售表现
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 3, flexDirection: 'column', gap: 1 }}>
          <Button
            onClick={handleTrainingConfirm}
            variant="contained"
            fullWidth
            sx={{
              py: 1.5,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              fontWeight: 600,
              borderRadius: '12px',
              '&:hover': {
                background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
              },
            }}
          >
            开始培训
          </Button>
          <Button
            onClick={() => {
              setTrainingDialog(false);
              setTraineeName('');
            }}
            variant="outlined"
            fullWidth
            sx={{
              py: 1.5,
              borderColor: 'rgba(255, 255, 255, 0.2)',
              color: '#fff',
              borderRadius: '12px',
            }}
          >
            取消
          </Button>
        </DialogActions>
      </Dialog>

      {/* Stage Completion Dialog */}
      <Dialog
        open={!!stageEvaluation}
        onClose={() => setStageEvaluation(null)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'rgba(26, 26, 46, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '20px',
          },
        }}
      >
        <DialogTitle sx={{ color: '#fff', textAlign: 'center' }}>
          <Box
            sx={{
              width: 60,
              height: 60,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
            }}
          >
            <Typography variant="h4" sx={{ color: '#fff', fontWeight: 700 }}>
              {stageEvaluation?.stage}
            </Typography>
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            阶段 {stageEvaluation?.stage} 完成
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
              得分
            </Typography>
            <Typography variant="h3" sx={{ color: '#43e97b', fontWeight: 700 }}>
              {stageEvaluation?.score}/5
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
              反馈
            </Typography>
            <Typography sx={{ color: '#fff', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
              {stageEvaluation?.feedback}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button
            onClick={() => setStageEvaluation(null)}
            variant="contained"
            fullWidth
            sx={{
              py: 1.5,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              fontWeight: 600,
              borderRadius: '12px',
              '&:hover': {
                background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
              },
            }}
          >
            继续培训
          </Button>
        </DialogActions>
      </Dialog>

      {/* Training Completion Dialog */}
      <Dialog
        open={trainingComplete}
        onClose={() => setTrainingComplete(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'rgba(26, 26, 46, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '20px',
          },
        }}
      >
        <DialogTitle sx={{ color: '#fff', textAlign: 'center' }}>
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
            }}
          >
            <SchoolIcon sx={{ fontSize: 48, color: '#fff' }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            培训完成！
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 3, textAlign: 'center' }}>
            恭喜您完成了所有5个阶段的销售培训
          </Typography>
          {finalEvaluation && (
            <Box sx={{ textAlign: 'center', mb: 2 }}>
              <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                总分
              </Typography>
              <Typography variant="h2" sx={{ color: '#43e97b', fontWeight: 700 }}>
                {finalEvaluation.scores?.total_score || 0}/25
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)', mt: 1 }}>
                {finalEvaluation.scores?.performance_level === 'excellent' && '优秀'}
                {finalEvaluation.scores?.performance_level === 'good' && '良好'}
                {finalEvaluation.scores?.performance_level === 'average' && '一般'}
                {finalEvaluation.scores?.performance_level === 'poor' && '需改进'}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3, flexDirection: 'column', gap: 1 }}>
          <Button
            onClick={() => {
              setTrainingComplete(false);
              stopAudio();  // 导航前停止音频
              if (finalEvaluation?.session_id) {
                navigate(`/training/evaluation?session_id=${finalEvaluation.session_id}`);
              }
            }}
            variant="contained"
            fullWidth
            sx={{
              py: 1.5,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              fontWeight: 600,
              borderRadius: '12px',
              '&:hover': {
                background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
              },
            }}
          >
            查看详细报告
          </Button>
          <Button
            onClick={() => {
              setTrainingComplete(false);
              handleExitTraining();
            }}
            variant="outlined"
            fullWidth
            sx={{
              py: 1.5,
              borderColor: 'rgba(255, 255, 255, 0.2)',
              color: '#fff',
              borderRadius: '12px',
            }}
          >
            返回主界面
          </Button>
        </DialogActions>
      </Dialog>

      {/* 错误提示 Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default DigitalCustomerPage;
