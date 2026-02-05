import React from 'react';
import { Box, Paper, Typography, Grid, Button } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';

const InterviewReport = ({ evaluation, session }) => {
  if (!evaluation) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>暂无评估数据</Typography>
      </Paper>
    );
  }

  const scores = [
    { label: '专业能力', value: evaluation.technical_score || 0 },
    { label: '沟通表达', value: evaluation.communication_score || 0 },
    { label: '问题解决', value: evaluation.problem_solving_score || 0 },
    { label: '文化契合', value: evaluation.cultural_fit_score || 0 }
  ];

  const handleExport = () => {
    // TODO: 实现PDF导出
    console.log('导出报告');
  };

  return (
    <Paper sx={{ p: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">面试评估报告</Typography>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={handleExport}
        >
          导出PDF
        </Button>
      </Box>

      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>基本信息</Typography>
        <Typography variant="body2">
          候选人: {session?.candidate_name || '未提供'}
        </Typography>
        <Typography variant="body2">
          面试官: {session?.interviewer_name || '未知'}
        </Typography>
        <Typography variant="body2">
          面试类型: {session?.interview_type || '未知'}
        </Typography>
      </Box>

      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>综合评估</Typography>
        <Grid container spacing={2}>
          {scores.map((score, index) => (
            <Grid item xs={6} sm={3} key={index}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#f5f5f5' }}>
                <Typography variant="h4" color="primary">
                  {score.value}
                </Typography>
                <Typography variant="body2">{score.label}</Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
        <Box sx={{ mt: 2, p: 2, bgcolor: '#e3f2fd', borderRadius: 2 }}>
          <Typography variant="h6">
            总分: {evaluation.total_score || 0}/40
          </Typography>
          <Typography variant="body1">
            表现等级: {evaluation.performance_level || '待评估'}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default InterviewReport;
