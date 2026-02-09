import React from 'react';
import {
  Alert,
  Card,
  CardContent,
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

/**
 * 简历风险提示组件
 * 显示简历中检测到的风险点
 */
const ResumeRiskAlert = ({ risks = [], qualityScore = 0 }) => {
  if (!risks || risks.length === 0) {
    return (
      <Alert
        severity="success"
        icon={<CheckCircleIcon />}
        sx={{ mb: 2 }}
      >
        <Typography variant="body2" fontWeight="medium">
          简历质量良好
        </Typography>
        <Typography variant="body2">
          未检测到明显风险点
        </Typography>
      </Alert>
    );
  }

  // 根据风险数量确定警告级别
  const getAlertSeverity = () => {
    if (risks.length >= 3) return 'error';
    if (risks.length >= 2) return 'warning';
    return 'info';
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <WarningIcon color="warning" />
          <Typography variant="subtitle2" fontWeight="bold">
            简历风险提示
          </Typography>
        </Box>

        <Box display="flex" flexDirection="column" gap={2}>
          <Alert severity={getAlertSeverity()}>
            检测到 {risks.length} 个风险点
          </Alert>

          <List dense>
            {risks.map((risk, index) => (
              <ListItem key={index} sx={{ px: 0 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <ErrorIcon color="warning" fontSize="small" />
                </ListItemIcon>
                <ListItemText primary={risk} />
              </ListItem>
            ))}
          </List>

          <Typography variant="body2" color="text.secondary">
            建议：在面试中针对这些风险点进行深入追问
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ResumeRiskAlert;
