import React, { useState } from 'react';
import {
  Button,
  Card,
  CardContent,
  Alert,
  Box,
  Typography,
  Snackbar,
  Alert as MuiAlert
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import axios from 'axios';
import { CONFIG } from '../../config';

/**
 * 批量导入候选人组件
 */
const BatchImportCandidates = () => {
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // 下载模板
  const downloadTemplate = () => {
    const template = [
      ['姓名', '邮箱', '电话', '职位'],
      ['张三', 'zhangsan@example.com', '13800138000', '软件工程师'],
      ['李四', 'lisi@example.com', '13900139000', '产品经理']
    ];

    const csvContent = template.map(row => row.join(',')).join('\n');
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = '候选人导入模板.csv';
    link.click();
  };

  // 处理文件上传
  const handleFileUpload = async (file) => {
    const isValidType = file.name.endsWith('.xlsx') ||
                        file.name.endsWith('.xls') ||
                        file.name.endsWith('.csv');
    if (!isValidType) {
      setSnackbar({ open: true, message: '仅支持 Excel 或 CSV 格式！', severity: 'error' });
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      await axios.post(`${CONFIG.API_BASE_URL}/digital-interviewer/candidates/batch-import`, formData);
      setSnackbar({ open: true, message: '导入成功', severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: '导入失败：' + error.message, severity: 'error' });
    } finally {
      setUploading(false);
    }
  };

  // 拖拽处理
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  return (
    <Card sx={{ maxWidth: 800, margin: '0 auto' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          批量导入候选人
        </Typography>

        <Box display="flex" flexDirection="column" gap={3}>
          {/* 说明 */}
          <Alert severity="info">
            <Typography variant="subtitle2" gutterBottom>导入说明</Typography>
            <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
              <li>支持 Excel (.xlsx, .xls) 和 CSV 格式</li>
              <li>必需列：姓名</li>
              <li>可选列：邮箱、电话、职位</li>
              <li>建议先下载模板，按照模板格式填写数据</li>
            </ul>
          </Alert>

          {/* 下载模板按钮 */}
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={downloadTemplate}
            sx={{ alignSelf: 'flex-start' }}
          >
            下载导入模板
          </Button>

          {/* 上传区域 */}
          <Box
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            sx={{
              border: '2px dashed',
              borderColor: dragActive ? 'primary.main' : 'grey.300',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              bgcolor: dragActive ? 'action.hover' : 'background.paper',
              cursor: 'pointer',
              transition: 'all 0.3s',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'action.hover'
              }
            }}
            onClick={() => document.getElementById('file-input').click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".xlsx,.xls,.csv"
              style={{ display: 'none' }}
              onChange={handleFileSelect}
            />
            <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="body1" gutterBottom>
              点击或拖拽文件到此区域上传
            </Typography>
            <Typography variant="body2" color="text.secondary">
              支持 Excel 和 CSV 格式
            </Typography>
            {uploading && (
              <Typography variant="body2" color="primary" sx={{ mt: 2 }}>
                上传中...
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <MuiAlert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity}>
          {snackbar.message}
        </MuiAlert>
      </Snackbar>
    </Card>
  );
};

export default BatchImportCandidates;
