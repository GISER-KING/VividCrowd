import React from 'react';
import {
  Card, CardContent, CardActions, Typography, Avatar,
  Chip, Box, IconButton, Tooltip
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import PersonIcon from '@mui/icons-material/Person';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import SchoolIcon from '@mui/icons-material/School';
import ElectricBoltIcon from '@mui/icons-material/ElectricBolt';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

const SOURCE_TYPE_CONFIG = {
  person: {
    label: '人物',
    icon: <PersonIcon sx={{ fontSize: 14 }} />,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    glow: 'rgba(102, 126, 234, 0.5)',
  },
  book: {
    label: '书籍',
    icon: <MenuBookIcon sx={{ fontSize: 14 }} />,
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    glow: 'rgba(67, 233, 123, 0.5)',
  },
  topic: {
    label: '专题',
    icon: <SchoolIcon sx={{ fontSize: 14 }} />,
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    glow: 'rgba(240, 147, 251, 0.5)',
  },
};

function CelebrityCard({ celebrity, selected, onSelect, onDelete }) {
  const sourceConfig = SOURCE_TYPE_CONFIG[celebrity.source_type] || SOURCE_TYPE_CONFIG.person;

  return (
    <Card
      sx={{
        cursor: 'pointer',
        background: selected
          ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)'
          : 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: selected
          ? '1px solid rgba(102, 126, 234, 0.6)'
          : '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '16px',
        boxShadow: selected
          ? '0 0 30px rgba(102, 126, 234, 0.3), inset 0 0 30px rgba(102, 126, 234, 0.1)'
          : '0 4px 20px rgba(0, 0, 0, 0.3)',
        transition: 'all 0.3s ease',
        position: 'relative',
        overflow: 'hidden',
        '&:hover': {
          border: '1px solid rgba(102, 126, 234, 0.4)',
          boxShadow: '0 8px 32px rgba(102, 126, 234, 0.25)',
          transform: 'translateY(-4px)',
          '& .card-glow': {
            opacity: 1,
          },
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: 'linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent)',
        },
      }}
      onClick={() => onSelect(celebrity)}
    >
      {/* 悬浮光效 */}
      <Box
        className="card-glow"
        sx={{
          position: 'absolute',
          top: '-50%',
          left: '-50%',
          width: '200%',
          height: '200%',
          background: 'radial-gradient(circle at center, rgba(102, 126, 234, 0.1) 0%, transparent 50%)',
          opacity: 0,
          transition: 'opacity 0.3s ease',
          pointerEvents: 'none',
        }}
      />

      {/* 选中指示器 */}
      {selected && (
        <Box
          sx={{
            position: 'absolute',
            top: 12,
            right: 12,
            width: 24,
            height: 24,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(102, 126, 234, 0.6)',
            animation: 'pulse 2s infinite',
          }}
        >
          <ElectricBoltIcon sx={{ fontSize: 14, color: '#fff' }} />
        </Box>
      )}

      <CardContent sx={{ pb: 1, position: 'relative', zIndex: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{ position: 'relative' }}>
            <Avatar
              sx={{
                background: sourceConfig.gradient,
                width: 52,
                height: 52,
                mr: 2,
                fontSize: '1.2rem',
                fontWeight: 700,
                boxShadow: `0 0 20px ${sourceConfig.glow}`,
                border: '2px solid rgba(255, 255, 255, 0.2)',
              }}
            >
              {celebrity.name[0]}
            </Avatar>
            {/* 头像光环 */}
            <Box
              sx={{
                position: 'absolute',
                top: -2,
                left: -2,
                right: -2,
                bottom: -2,
                borderRadius: '50%',
                border: `2px solid ${sourceConfig.glow}`,
                animation: selected ? 'glow 2s infinite' : 'none',
              }}
            />
          </Box>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 700,
                lineHeight: 1.2,
                color: '#fff',
                textShadow: selected ? '0 0 10px rgba(102, 126, 234, 0.5)' : 'none',
              }}
            >
              {celebrity.name}
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: 'rgba(255, 255, 255, 0.6)',
                display: 'block',
              }}
            >
              {celebrity.occupation || '未知职业'}
            </Typography>
          </Box>
        </Box>

        {/* 类型标签 */}
        <Chip
          icon={sourceConfig.icon}
          label={sourceConfig.label}
          size="small"
          sx={{
            mb: 2,
            background: `${sourceConfig.gradient}`,
            color: '#fff',
            fontWeight: 600,
            fontSize: '0.7rem',
            height: 24,
            boxShadow: `0 0 10px ${sourceConfig.glow}`,
            '& .MuiChip-icon': {
              color: '#fff',
            },
          }}
        />

        {celebrity.biography && (
          <Typography
            variant="body2"
            sx={{
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              fontSize: '0.8rem',
              color: 'rgba(255, 255, 255, 0.7)',
              lineHeight: 1.6,
              mb: 1,
            }}
          >
            {celebrity.biography}
          </Typography>
        )}

        {celebrity.famous_quotes && (
          <Box
            sx={{
              mt: 1.5,
              p: 1.5,
              borderRadius: '8px',
              background: 'rgba(102, 126, 234, 0.1)',
              border: '1px solid rgba(102, 126, 234, 0.2)',
              position: 'relative',
            }}
          >
            <AutoAwesomeIcon
              sx={{
                position: 'absolute',
                top: -8,
                left: 8,
                fontSize: 16,
                color: '#667eea',
                background: 'rgba(26, 26, 46, 1)',
                padding: '2px',
              }}
            />
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                fontStyle: 'italic',
                color: 'rgba(255, 255, 255, 0.6)',
                lineHeight: 1.5,
              }}
            >
              "{celebrity.famous_quotes.split('\n')[0]}"
            </Typography>
          </Box>
        )}
      </CardContent>

      <CardActions
        sx={{
          justifyContent: 'flex-end',
          pt: 0,
          px: 2,
          pb: 1.5,
          position: 'relative',
          zIndex: 1,
        }}
      >
        <Tooltip
          title="删除"
          arrow
          placement="top"
        >
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(celebrity);
            }}
            sx={{
              color: 'rgba(255, 255, 255, 0.4)',
              transition: 'all 0.3s ease',
              '&:hover': {
                color: '#f44336',
                background: 'rgba(244, 67, 54, 0.1)',
                boxShadow: '0 0 15px rgba(244, 67, 54, 0.3)',
              },
            }}
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </CardActions>
    </Card>
  );
}

export default CelebrityCard;
