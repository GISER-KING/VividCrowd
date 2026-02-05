import React, { useState } from 'react';
import { Box, Button, Typography, Alert } from '@mui/material';
import axios from 'axios';

const InterviewerUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('请选择文件');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        '/api/digital-interviewer/interviewers/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }

      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box sx={{ p: 3, border: '1px dashed #ccc', borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        上传面试官画像
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        支持PDF或Markdown格式
      </Typography>

      <input
        type="file"
        accept=".pdf,.md,.markdown"
        onChange={handleFileChange}
        style={{ display: 'none' }}
        id="profile-upload"
      />
      <label htmlFor="profile-upload">
        <Button variant="outlined" component="span" sx={{ mt: 2 }}>
          选择文件
        </Button>
      </label>

      {file && (
        <Typography variant="body2" sx={{ mt: 1 }}>
          已选择: {file.name}
        </Typography>
      )}

      <Button
        variant="contained"
        onClick={handleUpload}
        disabled={!file || uploading}
        sx={{ mt: 2, ml: 2 }}
      >
        {uploading ? '上传中...' : '上传'}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default InterviewerUpload;
