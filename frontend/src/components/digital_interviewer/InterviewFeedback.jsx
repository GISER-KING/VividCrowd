import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';

const InterviewFeedback = ({ evaluation }) => {
  if (!evaluation) {
    return (
      <Box sx={{ height: '100%' }}>
        <Typography variant="body2" color="text.secondary">
          回答问题后将显示评估结果
        </Typography>
      </Box>
    );
  }

  const scores = [
    { label: '专业能力', value: evaluation.technical_score || 0 },
    { label: '沟通表达', value: evaluation.communication_score || 0 },
    { label: '问题解决', value: evaluation.problem_solving_score || 0 },
    { label: '文化匹配', value: evaluation.cultural_fit_score || 0 }
  ];

  return (
    <Box sx={{ height: '100%' }}>
      {scores.map((score, index) => (
        <Box key={index} sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2">{score.label}</Typography>
            <Typography variant="body2" fontWeight="bold">
              {score.value}/10
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={(score.value / 10) * 100}
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>
      ))}

      <Box sx={{ mt: 2, p: 1.5, bgcolor: '#f5f5f5', borderRadius: 1 }}>
        <Typography variant="body2" fontWeight="bold" gutterBottom>
          整体质量
        </Typography>
        <Typography variant="body2">
          {evaluation.quality || '待评估'}
        </Typography>
      </Box>
    </Box>
  );
};

export default InterviewFeedback;
