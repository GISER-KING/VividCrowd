import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import RefreshIcon from '@mui/icons-material/Refresh';
import HomeIcon from '@mui/icons-material/Home';

/**
 * 错误回退界面组件
 * 显示友好的错误提示，与主题风格一致
 */
function ErrorFallback({ error, errorInfo, onRetry, onGoHome }) {
  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
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
          background: 'radial-gradient(circle at 30% 20%, rgba(244, 67, 54, 0.1) 0%, transparent 50%), radial-gradient(circle at 70% 80%, rgba(240, 147, 251, 0.08) 0%, transparent 50%)',
          pointerEvents: 'none',
        },
      }}
    >
      {/* 错误图标 */}
      <Box
        sx={{
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, rgba(244, 67, 54, 0.2) 0%, rgba(244, 67, 54, 0.1) 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 4,
          boxShadow: '0 0 60px rgba(244, 67, 54, 0.3)',
          animation: 'pulse 2s infinite ease-in-out',
          '@keyframes pulse': {
            '0%, 100%': { transform: 'scale(1)', opacity: 1 },
            '50%': { transform: 'scale(1.05)', opacity: 0.8 },
          },
        }}
      >
        <ErrorOutlineIcon sx={{ fontSize: 48, color: '#f44336' }} />
      </Box>

      {/* 错误标题 */}
      <Typography
        variant="h4"
        sx={{
          fontWeight: 700,
          background: 'linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.8) 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          mb: 2,
          textAlign: 'center',
        }}
      >
        哎呀，出了点问题
      </Typography>

      {/* 错误描述 */}
      <Typography
        sx={{
          color: 'rgba(255, 255, 255, 0.6)',
          mb: 4,
          maxWidth: 400,
          textAlign: 'center',
          lineHeight: 1.8,
        }}
      >
        页面遇到了一些意外情况，但别担心，
        <br />
        您可以尝试刷新页面或返回首页。
      </Typography>

      {/* 操作按钮 */}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          onClick={onRetry}
          startIcon={<RefreshIcon />}
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
          重试
        </Button>
        <Button
          variant="outlined"
          onClick={onGoHome}
          startIcon={<HomeIcon />}
          sx={{
            px: 4,
            py: 1.5,
            borderRadius: '12px',
            borderColor: 'rgba(255, 255, 255, 0.3)',
            color: 'rgba(255, 255, 255, 0.8)',
            fontWeight: 600,
            transition: 'all 0.3s ease',
            '&:hover': {
              borderColor: 'rgba(102, 126, 234, 0.6)',
              background: 'rgba(102, 126, 234, 0.1)',
              transform: 'translateY(-2px)',
            },
          }}
        >
          返回首页
        </Button>
      </Box>

      {/* 错误详情（开发模式显示） */}
      {process.env.NODE_ENV === 'development' && error && (
        <Box
          sx={{
            mt: 6,
            p: 3,
            maxWidth: 600,
            width: '90%',
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: '12px',
            border: '1px solid rgba(244, 67, 54, 0.2)',
          }}
        >
          <Typography
            variant="subtitle2"
            sx={{ color: '#f44336', mb: 1, fontWeight: 600 }}
          >
            错误详情（仅开发模式显示）
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: 'rgba(255, 255, 255, 0.5)',
              fontFamily: 'monospace',
              fontSize: '0.8rem',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
            }}
          >
            {error?.toString()}
          </Typography>
        </Box>
      )}
    </Box>
  );
}

export default ErrorFallback;
