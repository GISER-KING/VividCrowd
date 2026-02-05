import React from 'react';
import { Card, CardContent, Typography, Button, Box } from '@mui/material';

const InterviewerCard = ({ interviewer, onSelect, onDelete }) => {
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h6" gutterBottom>
          {interviewer.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {interviewer.title || '未设置职位'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {interviewer.company || '未设置公司'}
        </Typography>
      </CardContent>
      <Box sx={{ p: 2, pt: 0 }}>
        <Button
          variant="contained"
          fullWidth
          onClick={() => onSelect(interviewer)}
          sx={{ mb: 1 }}
        >
          开始面试
        </Button>
        <Button
          variant="outlined"
          color="error"
          fullWidth
          onClick={() => onDelete(interviewer.id)}
        >
          删除
        </Button>
      </Box>
    </Card>
  );
};

export default InterviewerCard;
