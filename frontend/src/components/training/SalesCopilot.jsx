import React, { useState, useRef, useEffect } from 'react';
import { Box, Typography, Paper, IconButton, Tooltip, TextField, Button, Avatar, CircularProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SmartToyIcon from '@mui/icons-material/SmartToy'; // Copilot Icon
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { CONFIG } from '../../config';

function SalesCopilot({ currentStage, suggestions = [], onUseSuggestion }) {
  const [messages, setMessages] = useState([
    { id: 1, type: 'bot', content: '你好！我是你的销售助手。你可以问我关于产品、话术或流程的问题，也可以上传资料让我学习。' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // 监听 suggestions 变化，如果有新建议，自动添加一条 bot 消息
  useEffect(() => {
    if (suggestions && suggestions.length > 0) {
      const suggestionMsg = {
        id: Date.now(),
        type: 'suggestion',
        content: '根据当前对话，我为你生成了一些建议话术：',
        items: suggestions
      };
      setMessages(prev => [...prev, suggestionMsg]);
    }
  }, [suggestions]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/digital-customer/knowledge/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
            id: Date.now(),
            type: 'system',
            content: `✅ 成功导入知识库：${data.filename} (解析 ${data.count} 条)`
        }]);
      } else {
        const errorData = await response.json();
        setMessages(prev => [...prev, {
            id: Date.now(),
            type: 'error',
            content: `❌ 上传失败: ${errorData.detail}`
        }]);
      }
    } catch (error) {
      console.error('Upload error:', error);
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'error',
        content: `❌ 网络错误，请重试`
    }]);
    } finally {
      setIsUploading(false);
      event.target.value = null;
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isQuerying) return;

    const userQuery = inputValue.trim();
    setInputValue('');
    
    // Add user message
    setMessages(prev => [...prev, { id: Date.now(), type: 'user', content: userQuery }]);
    setIsQuerying(true);

    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/digital-customer/knowledge/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: userQuery,
            stage: currentStage
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { id: Date.now() + 1, type: 'bot', content: data.answer }]);
      } else {
        setMessages(prev => [...prev, { id: Date.now() + 1, type: 'error', content: '抱歉，我现在无法回答这个问题。' }]);
      }
    } catch (error) {
        console.error("Query error", error);
        setMessages(prev => [...prev, { id: Date.now() + 1, type: 'error', content: '网络连接异常。' }]);
    } finally {
        setIsQuerying(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        accept=".xlsx,.pdf"
        onChange={handleFileChange}
      />

      <Paper
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          borderRadius: '16px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <Box sx={{ 
            p: 2, 
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
        }}>
            <Typography variant="subtitle1" sx={{ color: '#fff', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                <SmartToyIcon sx={{ color: '#43e97b' }} />
                销售助手
            </Typography>
            <Tooltip title="上传知识库文件 (pdf)">
                <IconButton 
                    size="small" 
                    onClick={handleUploadClick}
                    disabled={isUploading}
                    sx={{ color: 'rgba(255,255,255,0.7)', '&:hover': { color: '#fff', background: 'rgba(255,255,255,0.1)' } }}
                >
                    {isUploading ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
                </IconButton>
            </Tooltip>
        </Box>

        {/* Messages Area */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {messages.map((msg) => (
                <Box key={msg.id} sx={{ display: 'flex', flexDirection: 'column', alignItems: msg.type === 'user' ? 'flex-end' : 'flex-start' }}>
                    
                    {/* Message Bubble */}
                    <Box sx={{ 
                        maxWidth: '90%', 
                        display: 'flex', 
                        gap: 1,
                        flexDirection: msg.type === 'user' ? 'row-reverse' : 'row'
                    }}>
                        <Avatar 
                            sx={{ 
                                width: 28, height: 28, 
                                bgcolor: msg.type === 'user' ? '#667eea' : (msg.type === 'error' ? '#f44336' : '#43e97b') 
                            }}
                        >
                            {msg.type === 'user' ? <PersonIcon fontSize="small" /> : (msg.type === 'error' ? '!' : <SmartToyIcon fontSize="small" />)}
                        </Avatar>
                        
                        <Paper sx={{ 
                            p: 1.5, 
                            borderRadius: '12px',
                            bgcolor: msg.type === 'user' ? 'rgba(102, 126, 234, 0.2)' : 'rgba(255,255,255,0.05)',
                            color: '#fff',
                            borderTopLeftRadius: msg.type === 'bot' ? 0 : 12,
                            borderTopRightRadius: msg.type === 'user' ? 0 : 12
                        }}>
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
                                {msg.content}
                            </Typography>

                            {/* Suggestion Cards */}
                            {msg.type === 'suggestion' && msg.items && (
                                <Box sx={{ mt: 1.5, display: 'flex', flexDirection: 'column', gap: 1 }}>
                                    {msg.items.map((item, idx) => (
                                        <Paper
                                            key={idx}
                                            sx={{
                                                p: 1.5,
                                                bgcolor: 'rgba(67, 233, 123, 0.1)',
                                                border: '1px solid rgba(67, 233, 123, 0.3)',
                                                borderRadius: '8px',
                                                cursor: 'pointer',
                                                '&:hover': { bgcolor: 'rgba(67, 233, 123, 0.2)' },
                                                position: 'relative'
                                            }}
                                            onClick={() => onUseSuggestion && onUseSuggestion(item.script || item)}
                                        >
                                            {/* Rationale */}
                                            {item.rationale && (
                                                <Typography variant="caption" sx={{ color: '#43e97b', display: 'block', mb: 0.5, fontWeight: 600 }}>
                                                    💡 {item.rationale}
                                                </Typography>
                                            )}
                                            
                                            {/* Script */}
                                            <Typography variant="body2" sx={{ fontSize: '0.9rem', color: '#fff', lineHeight: 1.4 }}>
                                                {item.script || item}
                                            </Typography>
                                            
                                            <AutoAwesomeIcon sx={{ position: 'absolute', right: 8, top: 8, fontSize: 14, color: '#43e97b', opacity: 0.5 }} />
                                        </Paper>
                                    ))}
                                </Box>
                            )}
                        </Paper>
                    </Box>
                </Box>
            ))}
            {isQuerying && (
                <Box sx={{ display: 'flex', gap: 1 }}>
                     <Avatar sx={{ width: 28, height: 28, bgcolor: '#43e97b' }}><SmartToyIcon fontSize="small" /></Avatar>
                     <Paper sx={{ p: 1.5, borderRadius: '12px', bgcolor: 'rgba(255,255,255,0.05)' }}>
                        <CircularProgress size={16} sx={{ color: '#fff' }} />
                     </Paper>
                </Box>
            )}
            <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Box sx={{ p: 1.5, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
            <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField 
                    fullWidth 
                    size="small" 
                    placeholder="问点什么..." 
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    sx={{
                        '& .MuiOutlinedInput-root': {
                            color: '#fff',
                            bgcolor: 'rgba(0,0,0,0.2)',
                            '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                            '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                            '&.Mui-focused fieldset': { borderColor: '#43e97b' },
                        }
                    }}
                />
                <IconButton 
                    onClick={handleSend}
                    disabled={!inputValue.trim() || isQuerying}
                    sx={{ 
                        bgcolor: 'rgba(67, 233, 123, 0.2)', 
                        color: '#43e97b',
                        borderRadius: '8px',
                        '&:hover': { bgcolor: 'rgba(67, 233, 123, 0.3)' },
                        '&.Mui-disabled': { bgcolor: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.2)' }
                    }}
                >
                    <SendIcon fontSize="small" />
                </IconButton>
            </Box>
        </Box>
      </Paper>
    </Box>
  );
}

export default SalesCopilot;