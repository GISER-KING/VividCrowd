import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Chip,
  Snackbar,
  Alert
} from '@mui/material';
import {
  Replay as ReplayIcon,
  Warning as WarningIcon
} from '@mui/icons-material';

/**
 * 重新录制按钮组件
 * 允许候选人重新录制回答，最多2次
 */
const RetryRecordButton = ({
  roundNumber,
  retryCount = 0,
  maxRetries = 2,
  onRetry,
  disabled = false
}) => {
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // 计算剩余重录次数
  const remainingRetries = maxRetries - retryCount;
  const canRetry = remainingRetries > 0;

  // 打开确认对话框
  const handleOpenDialog = () => {
    setDialogOpen(true);
  };

  // 关闭确认对话框
  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  // 处理重录请求
  const handleConfirmRetry = async () => {
    setLoading(true);
    setDialogOpen(false);
    try {
      await onRetry(roundNumber);
      setSnackbar({ open: true, message: '已开始重新录制', severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: '重录失败：' + error.message, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // 关闭提示消息
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <>
      <Box display="flex" alignItems="center" gap={1}>
        <Button
          variant="outlined"
          startIcon={<ReplayIcon />}
          onClick={handleOpenDialog}
          disabled={!canRetry || disabled}
          loading={loading}
        >
          重新录制
        </Button>
        {canRetry ? (
          <Chip label={`剩余 ${remainingRetries} 次`} color="primary" size="small" />
        ) : (
          <Chip label="已用完" color="error" size="small" />
        )}
      </Box>

      {/* 确认对话框 */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog}>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <WarningIcon color="warning" />
            确认重新录制
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={1}>
            <Typography>您确定要重新录制这个问题的回答吗？</Typography>
            <Typography color="warning.main">
              剩余重录次数：{remainingRetries} 次
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>取消</Button>
          <Button onClick={handleConfirmRetry} variant="contained" autoFocus>
            确认重录
          </Button>
        </DialogActions>
      </Dialog>

      {/* 提示消息 */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default RetryRecordButton;
