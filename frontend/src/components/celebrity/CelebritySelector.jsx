import React from 'react';
import { Box, Typography, Grid, Chip, Paper } from '@mui/material';
import CelebrityCard from './CelebrityCard';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

function CelebritySelector({
  celebrities,
  selectedCelebrities,
  onSelect,
  onDelete,
  chatMode,
}) {
  const handleSelect = (celebrity) => {
    if (chatMode === 'private') {
      // 一对一模式：只能选择一个
      const isSelected = selectedCelebrities.some((c) => c.id === celebrity.id);
      if (isSelected) {
        onSelect([]);
      } else {
        onSelect([celebrity]);
      }
    } else {
      // 群聊模式：可以选择多个
      const isSelected = selectedCelebrities.some((c) => c.id === celebrity.id);
      if (isSelected) {
        onSelect(selectedCelebrities.filter((c) => c.id !== celebrity.id));
      } else {
        onSelect([...selectedCelebrities, celebrity]);
      }
    }
  };

  if (celebrities.length === 0) {
    return (
      <Paper
        sx={{
          p: 6,
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
        }}
      >
        <Box
          sx={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 3,
          }}
        >
          <AutoAwesomeIcon sx={{ fontSize: 36, color: '#667eea' }} />
        </Box>
        <Typography
          sx={{
            color: 'rgba(255, 255, 255, 0.6)',
            fontSize: '1rem',
          }}
        >
          暂无智囊数据，请先上传 PDF 文件添加智囊
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {/* 已选择区域 */}
      {selectedCelebrities.length > 0 && (
        <Box
          sx={{
            mb: 3,
            p: 2,
            borderRadius: '12px',
            background: 'rgba(102, 126, 234, 0.1)',
            border: '1px solid rgba(102, 126, 234, 0.2)',
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 1,
          }}
        >
          <Typography
            variant="body2"
            sx={{
              mr: 1,
              color: 'rgba(255, 255, 255, 0.6)',
              fontWeight: 500,
            }}
          >
            已选择:
          </Typography>
          {selectedCelebrities.map((c) => (
            <Chip
              key={c.id}
              label={c.name}
              onDelete={() => handleSelect(c)}
              size="small"
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: '#fff',
                fontWeight: 600,
                boxShadow: '0 0 10px rgba(102, 126, 234, 0.3)',
                '& .MuiChip-deleteIcon': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&:hover': {
                    color: '#fff',
                  },
                },
              }}
            />
          ))}
        </Box>
      )}

      {/* 卡片网格 */}
      <Grid container spacing={2.5}>
        {celebrities.map((celebrity) => (
          <Grid item xs={12} sm={6} md={4} key={celebrity.id}>
            <CelebrityCard
              celebrity={celebrity}
              selected={selectedCelebrities.some((c) => c.id === celebrity.id)}
              onSelect={handleSelect}
              onDelete={onDelete}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default CelebritySelector;
