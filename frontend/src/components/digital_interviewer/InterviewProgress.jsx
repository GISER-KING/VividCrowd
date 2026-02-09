import React from 'react';
import {
  Card,
  CardContent,
  LinearProgress,
  Box,
  Typography,
  Grid
} from '@mui/material';
import {
  AccessTime as ClockIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

/**
 * 面试进度显示组件
 */
const InterviewProgress = ({ currentRound, maxRounds, elapsedSeconds, status }) => {
  // 计算进度百分比
  const progressPercentage = maxRounds > 0 ? Math.round((currentRound / maxRounds) * 100) : 0;

  // 格式化时间显示
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // 进度条颜色
  const getProgressColor = () => {
    if (progressPercentage < 30) return 'success';
    if (progressPercentage < 70) return 'primary';
    return 'warning';
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
        <Box>
          {/* 标题和统计信息 */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="subtitle2" fontWeight="bold">
              面试进度
            </Typography>
            <Box display="flex" gap={3}>
              {/* 当前轮次 */}
              <Box textAlign="center">
                <Typography variant="caption" color="text.secondary" display="block">
                  当前轮次
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {currentRound} / {maxRounds}
                </Typography>
              </Box>
              {/* 已用时间 */}
              <Box textAlign="center">
                <Typography variant="caption" color="text.secondary" display="block">
                  已用时间
                </Typography>
                <Box display="flex" alignItems="center" gap={0.5}>
                  <ClockIcon sx={{ fontSize: 16 }} />
                  <Typography variant="body2" fontWeight="medium">
                    {formatTime(elapsedSeconds)}
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Box>

          {/* 进度条 */}
          <LinearProgress
            variant="determinate"
            value={progressPercentage}
            color={getProgressColor()}
            sx={{ height: 8, borderRadius: 1 }}
          />

          {/* 状态提示 */}
          {status === 'completed' && (
            <Box display="flex" alignItems="center" gap={0.5} mt={1}>
              <CheckCircleIcon color="success" sx={{ fontSize: 18 }} />
              <Typography variant="body2" color="success.main">
                面试已完成
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default InterviewProgress;
