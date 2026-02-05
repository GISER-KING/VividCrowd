import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer, List, ListItem, ListItemButton, ListItemIcon,
  ListItemText, Typography, Box, Divider
} from '@mui/material';
import GroupIcon from '@mui/icons-material/Group';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import PersonIcon from '@mui/icons-material/Person';
import WorkIcon from '@mui/icons-material/Work';

const DRAWER_WIDTH = 240;

const menuItems = [
  { path: '/', label: '智能群聊', icon: <GroupIcon />, description: 'AI 群体对话' },
  { path: '/celebrity', label: '数字分身', icon: <AutoAwesomeIcon />, description: '名人智囊团' },
  { path: '/customer-service', label: '数字客服', icon: <SupportAgentIcon />, description: '智能客服系统' },
  { path: '/digital-customer', label: '数字客户', icon: <PersonIcon />, description: '销售能力培训' },
  { path: '/digital-interviewer', label: '数字面试官', icon: <WorkIcon />, description: '面试能力训练' },
];

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          background: 'linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
          borderRight: '1px solid rgba(255, 255, 255, 0.08)',
          overflow: 'hidden',
        },
      }}
    >
      {/* Logo 区域 */}
      <Box
        sx={{
          p: 3,
          textAlign: 'center',
          position: 'relative',
          '&::after': {
            content: '""',
            position: 'absolute',
            bottom: 0,
            left: '10%',
            right: '10%',
            height: '1px',
            background: 'linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent)',
          },
        }}
      >
        {/* 发光 Logo */}
        <Box
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 56,
            height: 56,
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            boxShadow: '0 0 30px rgba(102, 126, 234, 0.5), 0 0 60px rgba(102, 126, 234, 0.3)',
            mb: 2,
            animation: 'float 6s ease-in-out infinite',
          }}
        >
          <Typography
            variant="h4"
            sx={{
              fontWeight: 900,
              color: '#fff',
              textShadow: '0 0 10px rgba(255,255,255,0.5)',
            }}
          >
            B
          </Typography>
        </Box>

        <Typography
          variant="h5"
          sx={{
            fontWeight: 700,
            background: 'linear-gradient(135deg, #667eea 0%, #f093fb 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '0.1em',
          }}
        >
          BizSoul
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: 'rgba(255,255,255,0.5)',
            letterSpacing: '0.2em',
            fontSize: '0.7rem',
          }}
        >
          AI 数字分身平台
        </Typography>
      </Box>

      {/* 菜单列表 */}
      <List sx={{ px: 2, mt: 2 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: '12px',
                  py: 1.5,
                  px: 2,
                  position: 'relative',
                  overflow: 'hidden',
                  background: isActive
                    ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%)'
                    : 'transparent',
                  border: isActive
                    ? '1px solid rgba(102, 126, 234, 0.5)'
                    : '1px solid transparent',
                  boxShadow: isActive
                    ? '0 0 20px rgba(102, 126, 234, 0.3), inset 0 0 20px rgba(102, 126, 234, 0.1)'
                    : 'none',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                    border: '1px solid rgba(102, 126, 234, 0.3)',
                    transform: 'translateX(4px)',
                  },
                  '&::before': isActive ? {
                    content: '""',
                    position: 'absolute',
                    left: 0,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    width: '3px',
                    height: '60%',
                    background: 'linear-gradient(180deg, #667eea, #f093fb)',
                    borderRadius: '0 4px 4px 0',
                    boxShadow: '0 0 10px rgba(102, 126, 234, 0.8)',
                  } : {},
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? '#667eea' : 'rgba(255,255,255,0.6)',
                    minWidth: 40,
                    '& svg': {
                      filter: isActive ? 'drop-shadow(0 0 8px rgba(102, 126, 234, 0.8))' : 'none',
                      transition: 'all 0.3s ease',
                    },
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  secondary={item.description}
                  primaryTypographyProps={{
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? '#fff' : 'rgba(255,255,255,0.8)',
                    fontSize: '0.95rem',
                  }}
                  secondaryTypographyProps={{
                    color: 'rgba(255,255,255,0.4)',
                    fontSize: '0.7rem',
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* 底部装饰 */}
      <Box sx={{ flexGrow: 1 }} />
      <Box
        sx={{
          p: 2,
          mx: 2,
          mb: 2,
          borderRadius: '12px',
          background: 'rgba(102, 126, 234, 0.1)',
          border: '1px solid rgba(102, 126, 234, 0.2)',
        }}
      >
        <Typography
          variant="caption"
          sx={{
            color: 'rgba(255,255,255,0.5)',
            display: 'block',
            textAlign: 'center',
          }}
        >
          Powered by
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: '#667eea',
            fontWeight: 600,
            textAlign: 'center',
            textShadow: '0 0 10px rgba(102, 126, 234, 0.5)',
          }}
        >
          Qwen AI
        </Typography>
      </Box>
    </Drawer>
  );
}

export default Sidebar;
