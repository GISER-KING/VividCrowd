import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import SignalWifiOffIcon from '@mui/icons-material/SignalWifiOff';
import SignalWifi4BarIcon from '@mui/icons-material/SignalWifi4Bar';
import SyncIcon from '@mui/icons-material/Sync';

/**
 * 连接状态指示器组件
 * 显示 WebSocket 连接状态
 */
function ConnectionStatus({
  isConnected,
  isReconnecting = false,
  retryCount = 0,
  maxRetries = 5
}) {
  if (isConnected) {
    return (
      <Chip
        icon={<SignalWifi4BarIcon sx={{ fontSize: 16 }} />}
        label="已连接"
        size="small"
        sx={{
          background: 'rgba(67, 233, 123, 0.15)',
          color: '#43e97b',
          border: '1px solid rgba(67, 233, 123, 0.3)',
          fontWeight: 600,
          '& .MuiChip-icon': {
            color: '#43e97b',
          },
        }}
      />
    );
  }

  if (isReconnecting) {
    return (
      <Chip
        icon={
          <SyncIcon
            sx={{
              fontSize: 16,
              animation: 'spin 1s linear infinite',
              '@keyframes spin': {
                '0%': { transform: 'rotate(0deg)' },
                '100%': { transform: 'rotate(360deg)' },
              },
            }}
          />
        }
        label={`重连中 (${retryCount}/${maxRetries})`}
        size="small"
        sx={{
          background: 'rgba(255, 152, 0, 0.15)',
          color: '#ff9800',
          border: '1px solid rgba(255, 152, 0, 0.3)',
          fontWeight: 600,
          '& .MuiChip-icon': {
            color: '#ff9800',
          },
        }}
      />
    );
  }

  return (
    <Chip
      icon={<SignalWifiOffIcon sx={{ fontSize: 16 }} />}
      label="连接断开"
      size="small"
      sx={{
        background: 'rgba(244, 67, 54, 0.15)',
        color: '#f44336',
        border: '1px solid rgba(244, 67, 54, 0.3)',
        fontWeight: 600,
        '& .MuiChip-icon': {
          color: '#f44336',
        },
      }}
    />
  );
}

export default ConnectionStatus;
