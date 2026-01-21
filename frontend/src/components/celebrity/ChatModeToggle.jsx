import React from 'react';
import { ToggleButton, ToggleButtonGroup, Typography, Box } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import GroupsIcon from '@mui/icons-material/Groups';

function ChatModeToggle({ mode, onChange }) {
  const handleChange = (event, newMode) => {
    if (newMode !== null) {
      onChange(newMode);
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
      <ToggleButtonGroup
        value={mode}
        exclusive
        onChange={handleChange}
        size="small"
        sx={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          p: 0.5,
          '& .MuiToggleButton-root': {
            px: 2,
            py: 0.75,
            border: 'none',
            borderRadius: '8px !important',
            color: 'rgba(255, 255, 255, 0.5)',
            fontWeight: 500,
            fontSize: '0.8rem',
            transition: 'all 0.3s ease',
            '&:hover': {
              background: 'rgba(102, 126, 234, 0.1)',
              color: 'rgba(255, 255, 255, 0.8)',
            },
            '&.Mui-selected': {
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#fff',
              boxShadow: '0 0 15px rgba(102, 126, 234, 0.4)',
              '&:hover': {
                background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
              },
            },
          },
        }}
      >
        <ToggleButton value="private">
          <PersonIcon sx={{ mr: 0.5, fontSize: '1rem' }} />
          一对一
        </ToggleButton>
        <ToggleButton value="group">
          <GroupsIcon sx={{ mr: 0.5, fontSize: '1rem' }} />
          智囊群聊
        </ToggleButton>
      </ToggleButtonGroup>
    </Box>
  );
}

export default ChatModeToggle;
