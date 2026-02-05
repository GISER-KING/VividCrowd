import React, { useState } from 'react';
import { Box, Button, Typography, Grid, Alert } from '@mui/material';
import axios from 'axios';

const VideoUpload = ({ interviewerId, onUploadSuccess }) => {
  const [videos, setVideos] = useState({
    idle: null,
    speaking: null,
    listening: null,
    thinking: null
  });
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const videoTypes = [
    { key: 'idle', label: '待机状态' },
    { key: 'speaking', label: '说话状态' },
    { key: 'listening', label: '倾听状态' },
    { key: 'thinking', label: '思考状态' }
  ];

  const handleFileChange = (type, event) => {
    const file = event.target.files[0];
    if (file) {
      setVideos(prev => ({ ...prev, [type]: file }));
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!Object.values(videos).some(v => v !== null)) {
      setError('请至少选择一个视频');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      Object.entries(videos).forEach(([key, file]) => {
        if (file) {
          formData.append(`video_${key}`, file);
        }
      });

      const response = await axios.post(
        `/api/digital-interviewer/interviewers/${interviewerId}/videos`,
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

      setVideos({ idle: null, speaking: null, listening: null, thinking: null });
    } catch (err) {
      setError(err.response?.data?.detail || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box sx={{ p: 3, border: '1px dashed #ccc', borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        上传数字人视频
      </Typography>

      <Grid container spacing={2} sx={{ mt: 1 }}>
        {videoTypes.map(({ key, label }) => (
          <Grid item xs={12} sm={6} key={key}>
            <Typography variant="body2" gutterBottom>
              {label}
            </Typography>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => handleFileChange(key, e)}
              style={{ display: 'none' }}
              id={`video-${key}`}
            />
            <label htmlFor={`video-${key}`}>
              <Button variant="outlined" component="span" size="small">
                选择视频
              </Button>
            </label>
            {videos[key] && (
              <Typography variant="caption" sx={{ ml: 1 }}>
                {videos[key].name}
              </Typography>
            )}
          </Grid>
        ))}
      </Grid>

      <Button
        variant="contained"
        onClick={handleUpload}
        disabled={uploading}
        sx={{ mt: 3 }}
      >
        {uploading ? '上传中...' : '上传视频'}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default VideoUpload;
