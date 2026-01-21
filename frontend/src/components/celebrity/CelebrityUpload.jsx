import React, { useState, useRef } from 'react';
import {
  Box, Button, Typography, Paper, CircularProgress,
  FormControl, InputLabel, Select, MenuItem, Alert
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import { CONFIG } from '../../config';

function CelebrityUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [sourceType, setSourceType] = useState('person');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    processFile(selectedFile);
  };

  const processFile = (selectedFile) => {
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        setError('请选择 PDF 文件');
        return;
      }
      setFile(selectedFile);
      setError('');
      setSuccess('');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    processFile(droppedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('请先选择文件');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', sourceType);

    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/celebrities/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '上传失败');
      }

      const result = await response.json();
      setSuccess(`成功添加: ${result.name}`);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onUploadSuccess && onUploadSuccess(result);
    } catch (err) {
      setError(err.message || '上传失败，请重试');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Paper
      sx={{
        p: 3,
        background: 'rgba(255, 255, 255, 0.03)',
        backdropFilter: 'blur(20px)',
        borderRadius: '20px',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: 'linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent)',
        },
      }}
    >
      {/* 标题区域 */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
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
            上传知识源
          </Typography>
          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
            支持人物资料、书籍内容、专题课程
          </Typography>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
        {/* 类型选择器 */}
        <FormControl
          size="small"
          sx={{
            minWidth: 200,
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
              },
            },
            '& .MuiInputLabel-root': {
              color: 'rgba(255, 255, 255, 0.5)',
              '&.Mui-focused': {
                color: '#667eea',
              },
            },
            '& .MuiSelect-icon': {
              color: 'rgba(255, 255, 255, 0.5)',
            },
          }}
        >
          <InputLabel>类型</InputLabel>
          <Select
            value={sourceType}
            label="类型"
            onChange={(e) => setSourceType(e.target.value)}
            MenuProps={{
              PaperProps: {
                sx: {
                  background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  '& .MuiMenuItem-root': {
                    color: '#fff',
                    '&:hover': {
                      background: 'rgba(102, 126, 234, 0.2)',
                    },
                    '&.Mui-selected': {
                      background: 'rgba(102, 126, 234, 0.3)',
                      '&:hover': {
                        background: 'rgba(102, 126, 234, 0.4)',
                      },
                    },
                  },
                },
              },
            }}
          >
            <MenuItem value="person">👤 人物资料</MenuItem>
            <MenuItem value="book">📚 书籍内容</MenuItem>
            <MenuItem value="topic">🎓 专题课程</MenuItem>
          </Select>
        </FormControl>

        {/* 上传区域 */}
        <Box
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          sx={{
            border: isDragging
              ? '2px solid #667eea'
              : file
              ? '2px solid rgba(67, 233, 123, 0.5)'
              : '2px dashed rgba(255, 255, 255, 0.2)',
            borderRadius: '16px',
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            background: isDragging
              ? 'rgba(102, 126, 234, 0.1)'
              : file
              ? 'rgba(67, 233, 123, 0.05)'
              : 'rgba(255, 255, 255, 0.02)',
            boxShadow: isDragging
              ? '0 0 30px rgba(102, 126, 234, 0.3), inset 0 0 30px rgba(102, 126, 234, 0.1)'
              : 'none',
            '&:hover': {
              border: '2px dashed rgba(102, 126, 234, 0.5)',
              background: 'rgba(102, 126, 234, 0.05)',
            },
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          {file ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Box
                sx={{
                  width: 64,
                  height: 64,
                  borderRadius: '16px',
                  background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mb: 2,
                  boxShadow: '0 0 20px rgba(67, 233, 123, 0.4)',
                }}
              >
                <InsertDriveFileIcon sx={{ fontSize: 32, color: '#fff' }} />
              </Box>
              <Typography sx={{ color: '#fff', fontWeight: 600, mb: 0.5 }}>
                {file.name}
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </Typography>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Box
                sx={{
                  width: 64,
                  height: 64,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mb: 2,
                  animation: isDragging ? 'pulse 1s infinite' : 'none',
                }}
              >
                <CloudUploadIcon sx={{ fontSize: 32, color: '#667eea' }} />
              </Box>
              <Typography sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 0.5 }}>
                点击或拖拽 PDF 文件到这里
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.4)' }}>
                支持 .pdf 格式
              </Typography>
            </Box>
          )}
        </Box>

        {/* 错误和成功提示 */}
        {error && (
          <Alert
            severity="error"
            sx={{
              background: 'rgba(244, 67, 54, 0.1)',
              border: '1px solid rgba(244, 67, 54, 0.3)',
              color: '#f44336',
              borderRadius: '12px',
              '& .MuiAlert-icon': {
                color: '#f44336',
              },
            }}
          >
            {error}
          </Alert>
        )}
        {success && (
          <Alert
            severity="success"
            icon={<CheckCircleIcon />}
            sx={{
              background: 'rgba(67, 233, 123, 0.1)',
              border: '1px solid rgba(67, 233, 123, 0.3)',
              color: '#43e97b',
              borderRadius: '12px',
              '& .MuiAlert-icon': {
                color: '#43e97b',
              },
            }}
          >
            {success}
          </Alert>
        )}

        {/* 上传按钮 */}
        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!file || uploading}
          startIcon={
            uploading ? (
              <CircularProgress size={20} sx={{ color: 'rgba(255,255,255,0.7)' }} />
            ) : (
              <CloudUploadIcon />
            )
          }
          sx={{
            py: 1.5,
            borderRadius: '12px',
            background: file && !uploading
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              : 'rgba(255, 255, 255, 0.1)',
            boxShadow: file && !uploading
              ? '0 0 20px rgba(102, 126, 234, 0.4)'
              : 'none',
            fontWeight: 600,
            fontSize: '1rem',
            transition: 'all 0.3s ease',
            '&:hover': {
              background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
              boxShadow: '0 0 30px rgba(102, 126, 234, 0.5)',
              transform: 'translateY(-2px)',
            },
            '&.Mui-disabled': {
              background: 'rgba(255, 255, 255, 0.05)',
              color: 'rgba(255, 255, 255, 0.3)',
            },
          }}
        >
          {uploading ? '解析中...' : '上传并解析'}
        </Button>

        {/* 说明文字 */}
        <Typography
          variant="caption"
          sx={{
            color: 'rgba(255, 255, 255, 0.4)',
            textAlign: 'center',
            lineHeight: 1.6,
          }}
        >
          系统将自动解析 PDF 内容，提取关键信息并生成数字分身
        </Typography>
      </Box>
    </Paper>
  );
}

export default CelebrityUpload;
