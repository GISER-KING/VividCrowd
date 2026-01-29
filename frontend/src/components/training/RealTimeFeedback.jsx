import React from 'react';
import { Box, Typography, Paper, Chip, Alert } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const QUALITY_CONFIG = {
  excellent: {
    label: '优秀',
    color: '#43e97b',
    bgColor: 'rgba(67, 233, 123, 0.15)',
    icon: <CheckCircleIcon />,
  },
  good: {
    label: '良好',
    color: '#38f9d7',
    bgColor: 'rgba(56, 249, 215, 0.15)',
    icon: <TrendingUpIcon />,
  },
  fair: {
    label: '一般',
    color: '#ffa726',
    bgColor: 'rgba(255, 167, 38, 0.15)',
    icon: <WarningIcon />,
  },
  poor: {
    label: '需改进',
    color: '#f44336',
    bgColor: 'rgba(244, 67, 54, 0.15)',
    icon: <ErrorIcon />,
  },
};

function RealTimeFeedback({ analysis, currentStage, currentRound }) {
  if (!analysis) {
    return (
      <Paper
        sx={{
          p: 3,
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          borderRadius: '16px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          height: '100%',
        }}
      >
        <Typography sx={{ color: 'rgba(255, 255, 255, 0.5)', textAlign: 'center' }}>
          发送消息后将显示实时反馈
        </Typography>
      </Paper>
    );
  }

  const qualityConfig = QUALITY_CONFIG[analysis.quality] || QUALITY_CONFIG.fair;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* 当前阶段信息 */}
      <Paper
        sx={{
          p: 2,
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          borderRadius: '16px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
        }}
      >
        <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
          当前进度
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Chip
            label={`阶段 ${currentStage}/5`}
            size="small"
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#fff',
              fontWeight: 600,
            }}
          />
          <Chip
            label={`第 ${currentRound} 轮`}
            size="small"
            sx={{
              background: 'rgba(255, 255, 255, 0.1)',
              color: '#fff',
            }}
          />
        </Box>
      </Paper>

      {/* 质量评价 */}
      <Paper
        sx={{
          p: 2.5,
          background: qualityConfig.bgColor,
          backdropFilter: 'blur(20px)',
          borderRadius: '16px',
          border: `1px solid ${qualityConfig.color}40`,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '12px',
              background: qualityConfig.color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
            }}
          >
            {qualityConfig.icon}
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              沟通质量
            </Typography>
            <Typography
              variant="h6"
              sx={{
                color: qualityConfig.color,
                fontWeight: 700,
              }}
            >
              {qualityConfig.label}
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* 发现的问题 */}
      {analysis.issues && analysis.issues.length > 0 && (
        <Paper
          sx={{
            p: 2.5,
            background: 'rgba(255, 167, 38, 0.1)',
            backdropFilter: 'blur(20px)',
            borderRadius: '16px',
            border: '1px solid rgba(255, 167, 38, 0.3)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <WarningIcon sx={{ color: '#ffa726', fontSize: 20 }} />
            <Typography
              variant="subtitle2"
              sx={{ color: '#ffa726', fontWeight: 700 }}
            >
              注意事项
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {analysis.issues.map((issue, idx) => (
              <Box
                key={idx}
                sx={{
                  p: 1.5,
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                  borderLeft: '3px solid #ffa726',
                }}
              >
                <Typography
                  variant="body2"
                  sx={{ color: 'rgba(255, 255, 255, 0.9)', lineHeight: 1.6 }}
                >
                  {issue}
                </Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      )}

      {/* 改进建议 */}
      {analysis.suggestions && analysis.suggestions.length > 0 && (
        <Paper
          sx={{
            p: 2.5,
            background: 'rgba(56, 249, 215, 0.1)',
            backdropFilter: 'blur(20px)',
            borderRadius: '16px',
            border: '1px solid rgba(56, 249, 215, 0.3)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <LightbulbIcon sx={{ color: '#38f9d7', fontSize: 20 }} />
            <Typography
              variant="subtitle2"
              sx={{ color: '#38f9d7', fontWeight: 700 }}
            >
              改进建议
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {analysis.suggestions.map((suggestion, idx) => (
              <Box
                key={idx}
                sx={{
                  p: 1.5,
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                  borderLeft: '3px solid #38f9d7',
                }}
              >
                <Typography
                  variant="body2"
                  sx={{ color: 'rgba(255, 255, 255, 0.9)', lineHeight: 1.6 }}
                >
                  {suggestion}
                </Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
}

export default RealTimeFeedback;
