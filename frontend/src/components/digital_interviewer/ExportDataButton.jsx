import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Snackbar,
  Alert
} from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { zhCN } from 'date-fns/locale';
import axios from 'axios';
import { CONFIG } from '../../config';

/**
 * 数据导出按钮组件
 */
const ExportDataButton = () => {
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // 处理导出
  const handleExport = async () => {
    setLoading(true);
    try {
      let url = `${CONFIG.API_BASE_URL}/digital-interviewer/interviews/export`;

      // 添加日期范围参数
      if (startDate && endDate) {
        const params = new URLSearchParams({
          start_date: startDate.toISOString().split('T')[0],
          end_date: endDate.toISOString().split('T')[0]
        });
        url += `?${params.toString()}`;
      }

      const response = await axios.get(url, {
        responseType: 'blob'
      });

      // 创建下载链接
      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `interview_results_${new Date().getTime()}.xlsx`;
      link.click();

      setSnackbar({ open: true, message: '导出成功', severity: 'success' });
      setModalVisible(false);
    } catch (error) {
      setSnackbar({ open: true, message: '导出失败：' + error.message, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={zhCN}>
      <Button
        variant="contained"
        startIcon={<DownloadIcon />}
        onClick={() => setModalVisible(true)}
      >
        导出数据
      </Button>

      <Dialog
        open={modalVisible}
        onClose={() => setModalVisible(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>导出面试数据</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <Box>选择日期范围（可选）：</Box>
            <DatePicker
              label="开始日期"
              value={startDate}
              onChange={setStartDate}
              slotProps={{ textField: { fullWidth: true } }}
            />
            <DatePicker
              label="结束日期"
              value={endDate}
              onChange={setEndDate}
              slotProps={{ textField: { fullWidth: true } }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModalVisible(false)}>取消</Button>
          <Button onClick={handleExport} variant="contained" disabled={loading}>
            {loading ? '导出中...' : '导出'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </LocalizationProvider>
  );
};

export default ExportDataButton;
