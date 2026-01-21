import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Chip,
  CircularProgress,
  Avatar,
  Stack,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Rating
} from '@mui/material';
import {
  Send as SendIcon,
  SupportAgent as SupportAgentIcon,
  Person as PersonIcon,
  Phone as PhoneIcon
} from '@mui/icons-material';
import { useCustomerServiceWS } from '../hooks/useCustomerServiceWS';
import { CONFIG } from '../config';

// 快捷回复选项
const QUICK_REPLIES = [
  '孩子挑食怎么办？',
  '维生素D需要补充吗？',
  '检测报告怎么看？',
  '益生菌什么时候吃？',
  '过敏体质怎么调理？'
];

// 匹配类型显示
const MATCH_TYPE_LABELS = {
  'high_confidence': { label: '精准匹配', color: 'success' },
  'mid_confidence': { label: '语义匹配', color: 'info' },
  'low_confidence': { label: '转人工', color: 'warning' },
  'no_match': { label: '无匹配', color: 'error' }
};

const CustomerServicePage = () => {
  const { messages, isConnected, sessionId, isLoading, sendMessage } = useCustomerServiceWS();
  const [inputValue, setInputValue] = useState('');
  const [ratingDialogOpen, setRatingDialogOpen] = useState(false);
  const [userRating, setUserRating] = useState(0);
  const messagesEndRef = useRef(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
      sendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickReply = (text) => {
    if (!isLoading) {
      sendMessage(text);
    }
  };

  const handleRatingSubmit = async () => {
    if (sessionId && userRating > 0) {
      try {
        const formData = new FormData();
        formData.append('rating', userRating);

        await fetch(`${CONFIG.API_BASE_URL}/customer-service/session/${sessionId}/rating`, {
          method: 'POST',
          body: formData
        });
      } catch (error) {
        console.error('Rating error:', error);
      }
    }
    setRatingDialogOpen(false);
  };

  return (
    <Box sx={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%)'
    }}>
      {/* 头部 */}
      <Paper sx={{
        p: 2,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        borderRadius: 0,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Avatar sx={{ bgcolor: 'white' }}>
          <SupportAgentIcon sx={{ color: '#667eea' }} />
        </Avatar>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h6" sx={{ color: 'white' }}>
            智能客服
          </Typography>
          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
            {isConnected ? '在线' : '离线'}
            {sessionId && ` | 会话: ${sessionId.slice(0, 8)}...`}
          </Typography>
        </Box>
        <IconButton
          sx={{ color: 'white' }}
          onClick={() => setRatingDialogOpen(true)}
          title="评价服务"
        >
          <PhoneIcon />
        </IconButton>
      </Paper>

      {/* 消息区域 */}
      <Box sx={{
        flexGrow: 1,
        overflow: 'auto',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        {/* 欢迎消息 */}
        {messages.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Avatar sx={{
              width: 80,
              height: 80,
              margin: 'auto',
              mb: 2,
              bgcolor: '#667eea',
              boxShadow: '0 0 30px rgba(102, 126, 234, 0.5)'
            }}>
              <SupportAgentIcon sx={{ fontSize: 48 }} />
            </Avatar>
            <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.9)' }} gutterBottom>
              您好！我是您的专属健康管理客服
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              可以解答您关于儿童营养、饮食调理、检测报告解读等方面的问题
            </Typography>
          </Box>
        )}

        {/* 消息列表 */}
        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              alignItems: 'flex-start',
              gap: 1
            }}
          >
            {/* 客服头像 */}
            {msg.sender === 'bot' && (
              <Avatar sx={{ bgcolor: '#667eea', width: 36, height: 36 }}>
                <SupportAgentIcon sx={{ fontSize: 20 }} />
              </Avatar>
            )}

            <Box sx={{ maxWidth: '70%' }}>
              {/* 消息气泡 */}
              <Paper
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  bgcolor: msg.sender === 'user' ? undefined : 'rgba(255,255,255,0.95)',
                  background: msg.sender === 'user'
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : undefined,
                  color: msg.sender === 'user' ? 'white' : '#1a1a1a',
                  boxShadow: msg.sender === 'user'
                    ? '0 0 20px rgba(102, 126, 234, 0.3)'
                    : '0 2px 8px rgba(0,0,0,0.1)'
                }}
              >
                <Typography
                  variant="body1"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}
                >
                  {msg.content}
                </Typography>
              </Paper>
            </Box>

            {/* 用户头像 */}
            {msg.sender === 'user' && (
              <Avatar sx={{ bgcolor: '#4caf50', width: 36, height: 36 }}>
                <PersonIcon sx={{ fontSize: 20 }} />
              </Avatar>
            )}
          </Box>
        ))}

        <div ref={messagesEndRef} />
      </Box>

      {/* 快捷回复 */}
      <Box sx={{ px: 2, pb: 1 }}>
        <Stack
          direction="row"
          spacing={1}
          sx={{
            overflowX: 'auto',
            pb: 1,
            '&::-webkit-scrollbar': { height: 4 },
            '&::-webkit-scrollbar-thumb': { bgcolor: 'rgba(102, 126, 234, 0.5)', borderRadius: 2 }
          }}
        >
          {QUICK_REPLIES.map((text, index) => (
            <Chip
              key={index}
              label={text}
              onClick={() => handleQuickReply(text)}
              disabled={isLoading}
              sx={{
                cursor: 'pointer',
                bgcolor: 'rgba(102, 126, 234, 0.2)',
                color: 'rgba(255,255,255,0.9)',
                border: '1px solid rgba(102, 126, 234, 0.3)',
                '&:hover': {
                  bgcolor: 'rgba(102, 126, 234, 0.3)',
                  borderColor: 'rgba(102, 126, 234, 0.5)'
                },
                '&.Mui-disabled': {
                  opacity: 0.5
                }
              }}
            />
          ))}
        </Stack>
      </Box>

      {/* 输入区域 */}
      <Paper sx={{
        p: 2,
        borderRadius: 0,
        background: 'rgba(15, 12, 41, 0.8)',
        backdropFilter: 'blur(10px)',
        borderTop: '1px solid rgba(102, 126, 234, 0.2)'
      }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            placeholder="请输入您的问题..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={!isConnected || isLoading}
            multiline
            maxRows={3}
            size="small"
            InputProps={{
              style: {
                color: '#1a1a1a',
                backgroundColor: 'rgba(255,255,255,0.95)',
                borderRadius: '12px'
              }
            }}
            inputProps={{
              style: {
                color: '#1a1a1a'
              }
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                bgcolor: 'rgba(255,255,255,0.95)',
                '& fieldset': {
                  borderColor: 'rgba(102, 126, 234, 0.3)'
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(102, 126, 234, 0.5)'
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#667eea'
                }
              },
              '& .MuiInputBase-input::placeholder': {
                color: 'rgba(0,0,0,0.5)',
                opacity: 1
              }
            }}
          />
          <IconButton
            onClick={handleSend}
            disabled={!inputValue.trim() || !isConnected || isLoading}
            sx={{
              bgcolor: '#667eea',
              color: 'white',
              '&:hover': { bgcolor: '#5a6fd6' },
              '&:disabled': { bgcolor: 'grey.300' }
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>

      {/* 评分对话框 */}
      <Dialog open={ratingDialogOpen} onClose={() => setRatingDialogOpen(false)}>
        <DialogTitle>评价本次服务</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 2 }}>
            <Rating
              value={userRating}
              onChange={(e, newValue) => setUserRating(newValue)}
              size="large"
            />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {userRating > 0 ? `您选择了 ${userRating} 星` : '点击星星评分'}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRatingDialogOpen(false)}>取消</Button>
          <Button onClick={handleRatingSubmit} variant="contained" disabled={userRating === 0}>
            提交
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CustomerServicePage;
