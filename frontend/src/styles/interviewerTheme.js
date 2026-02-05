/**
 * 数字面试官 - 商务科技风格主题
 * 深色玻璃拟态设计，青蓝色调高亮
 */

// 主题色彩
export const theme = {
  // 背景色
  bgPrimary: '#0a0e17',
  bgSecondary: '#0d1321',
  bgTertiary: '#131a2b',
  bgCard: 'rgba(19, 26, 43, 0.7)',
  bgGlass: 'rgba(255, 255, 255, 0.03)',

  // 主色调 - 青蓝渐变
  primary: '#00d4ff',
  primaryDark: '#0099cc',
  primaryGlow: 'rgba(0, 212, 255, 0.15)',

  // 强调色
  accent: '#7c3aed',
  accentGlow: 'rgba(124, 58, 237, 0.2)',

  // 成功/警告/错误
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',

  // 文字色
  textPrimary: '#f1f5f9',
  textSecondary: '#94a3b8',
  textMuted: '#64748b',

  // 边框
  border: 'rgba(255, 255, 255, 0.08)',
  borderHover: 'rgba(0, 212, 255, 0.3)',
  borderActive: 'rgba(0, 212, 255, 0.6)',

  // 渐变
  gradientPrimary: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
  gradientCard: 'linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 100%)',
  gradientBorder: 'linear-gradient(135deg, rgba(0,212,255,0.5) 0%, rgba(124,58,237,0.5) 100%)',
};

// 通用样式
export const styles = {
  // 页面容器
  pageContainer: {
    minHeight: '100vh',
    background: `
      radial-gradient(ellipse at 20% 0%, rgba(0, 212, 255, 0.08) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 100%, rgba(124, 58, 237, 0.08) 0%, transparent 50%),
      linear-gradient(180deg, ${theme.bgPrimary} 0%, ${theme.bgSecondary} 100%)
    `,
    backgroundAttachment: 'fixed',
    position: 'relative',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundImage: `
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)
      `,
      backgroundSize: '50px 50px',
      pointerEvents: 'none',
    },
  },

  // 玻璃卡片
  glassCard: {
    background: theme.bgCard,
    backdropFilter: 'blur(20px)',
    border: `1px solid ${theme.border}`,
    borderRadius: '16px',
    position: 'relative',
    overflow: 'hidden',
    transition: 'all 0.3s ease',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      height: '1px',
      background: theme.gradientBorder,
      opacity: 0.5,
    },
    '&:hover': {
      border: `1px solid ${theme.borderHover}`,
      boxShadow: `0 8px 32px rgba(0, 212, 255, 0.1)`,
    },
  },

  // 发光卡片（选中状态）
  glowCard: {
    background: theme.bgCard,
    backdropFilter: 'blur(20px)',
    border: `1px solid ${theme.borderActive}`,
    borderRadius: '16px',
    boxShadow: `
      0 0 20px rgba(0, 212, 255, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.1)
    `,
    position: 'relative',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      height: '2px',
      background: theme.gradientPrimary,
    },
  },

  // 主按钮
  primaryButton: {
    background: theme.gradientPrimary,
    color: '#fff',
    fontWeight: 600,
    padding: '12px 32px',
    borderRadius: '12px',
    border: 'none',
    textTransform: 'none',
    fontSize: '15px',
    letterSpacing: '0.5px',
    boxShadow: '0 4px 20px rgba(0, 212, 255, 0.3)',
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 8px 30px rgba(0, 212, 255, 0.4)',
    },
    '&:disabled': {
      background: theme.textMuted,
      boxShadow: 'none',
    },
  },

  // 次要按钮
  secondaryButton: {
    background: 'transparent',
    color: theme.primary,
    fontWeight: 500,
    padding: '10px 24px',
    borderRadius: '10px',
    border: `1px solid ${theme.borderHover}`,
    textTransform: 'none',
    transition: 'all 0.3s ease',
    '&:hover': {
      background: theme.primaryGlow,
      borderColor: theme.primary,
    },
  },

  // 输入框
  inputField: {
    '& .MuiOutlinedInput-root': {
      background: 'rgba(255, 255, 255, 0.03)',
      borderRadius: '10px',
      color: theme.textPrimary,
      '& fieldset': {
        borderColor: theme.border,
      },
      '&:hover fieldset': {
        borderColor: theme.borderHover,
      },
      '&.Mui-focused fieldset': {
        borderColor: theme.primary,
        borderWidth: '1px',
      },
    },
    '& .MuiInputLabel-root': {
      color: theme.textSecondary,
    },
    '& .MuiInputLabel-root.Mui-focused': {
      color: theme.primary,
    },
    '& .MuiSelect-icon': {
      color: theme.textSecondary,
    },
  },

  // 标题样式
  pageTitle: {
    fontSize: '2.5rem',
    fontWeight: 700,
    background: theme.gradientPrimary,
    backgroundClip: 'text',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    letterSpacing: '-0.5px',
    marginBottom: '8px',
  },

  // 副标题
  subtitle: {
    color: theme.textSecondary,
    fontSize: '1rem',
    letterSpacing: '0.5px',
  },

  // Tab样式
  tabContainer: {
    borderBottom: `1px solid ${theme.border}`,
    '& .MuiTab-root': {
      color: theme.textSecondary,
      textTransform: 'none',
      fontSize: '15px',
      fontWeight: 500,
      minHeight: '56px',
      transition: 'all 0.3s ease',
      '&:hover': {
        color: theme.textPrimary,
      },
      '&.Mui-selected': {
        color: theme.primary,
      },
    },
    '& .MuiTabs-indicator': {
      background: theme.gradientPrimary,
      height: '3px',
      borderRadius: '3px 3px 0 0',
    },
  },

  // 状态指示器
  statusIndicator: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '6px 12px',
    borderRadius: '20px',
    fontSize: '13px',
    fontWeight: 500,
  },

  statusConnected: {
    background: 'rgba(16, 185, 129, 0.15)',
    color: theme.success,
    border: `1px solid rgba(16, 185, 129, 0.3)`,
  },

  statusDisconnected: {
    background: 'rgba(239, 68, 68, 0.15)',
    color: theme.error,
    border: `1px solid rgba(239, 68, 68, 0.3)`,
  },

  // 消息气泡 - 面试官
  messageBubbleInterviewer: {
    background: 'rgba(0, 212, 255, 0.1)',
    border: `1px solid rgba(0, 212, 255, 0.2)`,
    borderRadius: '16px 16px 16px 4px',
    padding: '16px',
    maxWidth: '85%',
    animation: 'fadeInLeft 0.3s ease',
  },

  // 消息气泡 - 候选人
  messageBubbleCandidate: {
    background: 'rgba(124, 58, 237, 0.1)',
    border: `1px solid rgba(124, 58, 237, 0.2)`,
    borderRadius: '16px 16px 4px 16px',
    padding: '16px',
    maxWidth: '85%',
    marginLeft: 'auto',
    animation: 'fadeInRight 0.3s ease',
  },

  // 视频容器
  videoContainer: {
    position: 'relative',
    borderRadius: '12px',
    overflow: 'hidden',
    background: '#000',
    '&::after': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      border: `1px solid ${theme.border}`,
      borderRadius: '12px',
      pointerEvents: 'none',
    },
  },

  // 评分条
  scoreBar: {
    height: '6px',
    borderRadius: '3px',
    background: 'rgba(255, 255, 255, 0.1)',
    overflow: 'hidden',
    '& .MuiLinearProgress-bar': {
      background: theme.gradientPrimary,
      borderRadius: '3px',
    },
  },

  // 脉冲动画（录音状态）
  pulseAnimation: {
    animation: 'pulse 2s infinite',
    '@keyframes pulse': {
      '0%': {
        boxShadow: '0 0 0 0 rgba(239, 68, 68, 0.4)',
      },
      '70%': {
        boxShadow: '0 0 0 20px rgba(239, 68, 68, 0)',
      },
      '100%': {
        boxShadow: '0 0 0 0 rgba(239, 68, 68, 0)',
      },
    },
  },
};

// 全局CSS动画
export const globalAnimations = `
  @keyframes fadeInLeft {
    from {
      opacity: 0;
      transform: translateX(-20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes fadeInRight {
    from {
      opacity: 0;
      transform: translateX(20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes glow {
    0%, 100% {
      box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }
    50% {
      box-shadow: 0 0 40px rgba(0, 212, 255, 0.5);
    }
  }

  @keyframes shimmer {
    0% {
      background-position: -200% 0;
    }
    100% {
      background-position: 200% 0;
    }
  }
`;

export default { theme, styles, globalAnimations };
