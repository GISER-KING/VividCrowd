import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Button,
  Divider,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Menu,
  MenuItem,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DownloadIcon from '@mui/icons-material/Download';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import RadarChart from '../../components/training/RadarChart';
import { CONFIG } from '../../config';

// 打印样式
const printStyles = `
  @media print {
    /* 隐藏不需要打印的元素 */
    .no-print {
      display: none !important;
    }

    /* 页面设置 */
    @page {
      size: A4;
      margin: 1.5cm;
    }

    /* 重置背景色以节省墨水 */
    body {
      background: white !important;
    }

    /* 确保内容适应页面 */
    * {
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }

    /* 避免在小元素内部分页 */
    .avoid-break {
      page-break-inside: avoid;
      break-inside: avoid;
    }

    /* 允许大容器分页 */
    .allow-break {
      page-break-inside: auto;
      break-inside: auto;
    }

    /* 手风琴默认展开 */
    .MuiAccordion-root {
      box-shadow: none !important;
      page-break-inside: auto !important;
      break-inside: auto !important;
    }

    .MuiAccordionDetails-root {
      display: block !important;
    }

    /* 优化边距 */
    .print-optimize {
      padding: 8px !important;
      margin-bottom: 12px !important;
    }

    /* 确保内容可见 */
    .MuiGrid-root {
      page-break-inside: auto;
    }
  }
`;


const TASK_NAMES = {
  trust_building_score: '信任与关系建立',
  needs_diagnosis_score: '信息探索与需求诊断',
  value_presentation_score: '价值呈现与方案链接',
  objection_handling_score: '异议/顾虑处理管理',
  progress_management_score: '进程推进与节奏管理',
};

const PERFORMANCE_LEVELS = {
  excellent: { label: '优秀', color: '#43e97b', bgColor: 'rgba(67, 233, 123, 0.15)' },
  good: { label: '良好', color: '#38f9d7', bgColor: 'rgba(56, 249, 215, 0.15)' },
  average: { label: '一般', color: '#ffa726', bgColor: 'rgba(255, 167, 38, 0.15)' },
  poor: { label: '需改进', color: '#f44336', bgColor: 'rgba(244, 67, 54, 0.15)' },
};

function EvaluationReportPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { evaluation: initialEvaluation } = location.state || {};

  // 混合提取 sessionId：优先使用 location.state，其次使用查询参数
  const getSessionId = () => {
    // 优先：location.state（程序化导航）
    if (location.state?.sessionId) {
      return location.state.sessionId;
    }

    // 备选：查询参数（支持直接 URL 访问和刷新）
    const searchParams = new URLSearchParams(location.search);
    const querySessionId = searchParams.get('session_id');
    if (querySessionId) {
      return querySessionId;
    }

    return null;
  };

  const sessionId = getSessionId();

  const [evaluation, setEvaluation] = useState(initialEvaluation);
  const [loading, setLoading] = useState(!initialEvaluation);
  const [downloadMenuAnchor, setDownloadMenuAnchor] = useState(null);

  useEffect(() => {
    if (!sessionId) {
      navigate('/digital-customer');
      return;
    }

    if (!initialEvaluation) {
      fetchEvaluation();
    }
  }, [sessionId]);

  const fetchEvaluation = async () => {
    try {
      const response = await fetch(
        `${CONFIG.API_BASE_URL}/digital-customer/training/sessions/${sessionId}/evaluation`
      );
      if (response.ok) {
        const data = await response.json();
        setEvaluation(data);
      }
    } catch (err) {
      console.error('Failed to fetch evaluation:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    await downloadReport('markdown');
  };

  const handleDownloadPDF = async () => {
    await downloadReport('pdf');
  };

  const downloadReport = async (format) => {
    try {
      const endpoint = format === 'pdf'
        ? `${CONFIG.API_BASE_URL}/digital-customer/training/sessions/${sessionId}/download-pdf`
        : `${CONFIG.API_BASE_URL}/digital-customer/training/sessions/${sessionId}/download-report`;

      const response = await fetch(endpoint);

      if (!response.ok) {
        throw new Error('下载失败');
      }

      // 获取文件名（从响应头中提取）
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `培训报告_${sessionId}.${format === 'pdf' ? 'pdf' : 'md'}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)|filename="(.+)"/);
        if (filenameMatch) {
          filename = decodeURIComponent(filenameMatch[1] || filenameMatch[2]);
        }
      }

      // 创建 Blob 并触发下载
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      // 关闭菜单
      setDownloadMenuAnchor(null);
    } catch (error) {
      console.error('下载报告失败:', error);
      alert('下载报告失败，请稍后重试');
    }
  };

  const handleOpenDownloadMenu = (event) => {
    setDownloadMenuAnchor(event.currentTarget);
  };

  const handleCloseDownloadMenu = () => {
    setDownloadMenuAnchor(null);
  };

  if (loading) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)',
        }}
      >
        <Typography sx={{ color: '#fff' }}>加载评价报告中...</Typography>
      </Box>
    );
  }

  if (!evaluation) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)',
        }}
      >
        <Typography sx={{ color: '#fff' }}>未找到评价报告</Typography>
      </Box>
    );
  }

  const performanceLevel = PERFORMANCE_LEVELS[evaluation.scores?.performance_level] || PERFORMANCE_LEVELS.average;

  return (
    <Box
      sx={{
        height: '100%',
        overflow: 'auto',
        background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)',
      }}
    >
      {/* 注入打印样式 */}
      <style>{printStyles}</style>

      {/* Header */}
      <Paper
        className="no-print"
        elevation={0}
        sx={{
          p: 3,
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/digital-customer')}
              sx={{ color: '#fff' }}
            >
              返回
            </Button>
            <Box>
              <Typography variant="h5" sx={{ color: '#fff', fontWeight: 700 }}>
                培训评价报告
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                {evaluation.trainee_name} | {evaluation.scenario_name}
              </Typography>
            </Box>
          </Box>
          <Box>
            <Button
              startIcon={<DownloadIcon />}
              endIcon={<ArrowDropDownIcon />}
              onClick={handleOpenDownloadMenu}
              variant="outlined"
              sx={{
                borderColor: 'rgba(255, 255, 255, 0.2)',
                color: '#fff',
                '&:hover': {
                  borderColor: '#667eea',
                  background: 'rgba(102, 126, 234, 0.1)',
                },
              }}
            >
              下载报告
            </Button>
            <Menu
              anchorEl={downloadMenuAnchor}
              open={Boolean(downloadMenuAnchor)}
              onClose={handleCloseDownloadMenu}
              PaperProps={{
                sx: {
                  background: 'rgba(30, 30, 50, 0.95)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  mt: 1,
                },
              }}
            >
              <MenuItem
                onClick={handleDownloadReport}
                sx={{
                  color: '#fff',
                  '&:hover': {
                    background: 'rgba(102, 126, 234, 0.2)',
                  },
                }}
              >
                <DownloadIcon sx={{ mr: 1, fontSize: 20 }} />
                下载 Markdown (.md)
              </MenuItem>
              <MenuItem
                onClick={handleDownloadPDF}
                sx={{
                  color: '#fff',
                  '&:hover': {
                    background: 'rgba(102, 126, 234, 0.2)',
                  },
                }}
              >
                <DownloadIcon sx={{ mr: 1, fontSize: 20 }} />
                下载 PDF (.pdf)
              </MenuItem>
            </Menu>
          </Box>
        </Box>
      </Paper>

      {/* Content */}
      <Box sx={{ p: 4 }}>
        <Grid container spacing={3}>
          {/* Overall Score */}
          <Grid item xs={12} className="avoid-break">
            <Paper
              className="print-optimize"
              sx={{
                p: 4,
                background: performanceLevel.bgColor,
                backdropFilter: 'blur(20px)',
                borderRadius: '20px',
                border: `1px solid ${performanceLevel.color}40`,
                textAlign: 'center',
              }}
            >
              <Typography variant="h3" sx={{ color: performanceLevel.color, fontWeight: 700, mb: 1 }}>
                {evaluation.scores?.total_score || 0}/25
              </Typography>
              <Chip
                label={performanceLevel.label}
                sx={{
                  background: performanceLevel.color,
                  color: '#fff',
                  fontWeight: 700,
                  fontSize: '1rem',
                  px: 2,
                  py: 0.5,
                }}
              />
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mt: 2 }}>
                培训时长: {evaluation.duration_minutes} 分钟 | 完成时间: {new Date(evaluation.completed_at).toLocaleString()}
              </Typography>
            </Paper>
          </Grid>

          {/* Radar Chart */}
          <Grid item xs={12} md={6} className="avoid-break">
            <RadarChart scores={evaluation.scores} />
          </Grid>

          {/* Score Breakdown */}
          <Grid item xs={12} md={6} className="avoid-break">
            <Paper
              className="print-optimize"
              sx={{
                p: 3,
                background: 'rgba(255, 255, 255, 0.03)',
                backdropFilter: 'blur(20px)',
                borderRadius: '20px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                height: '100%',
              }}
            >
              <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700, mb: 3 }}>
                各项得分详情
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {Object.entries(TASK_NAMES).map(([key, name]) => {
                  const score = evaluation.scores[key] || 0;
                  const percentage = (score / 5) * 100;
                  return (
                    <Box key={key}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" sx={{ color: '#fff', fontWeight: 600 }}>
                          {name}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#43e97b', fontWeight: 700 }}>
                          {score}/5
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          height: 8,
                          background: 'rgba(255, 255, 255, 0.1)',
                          borderRadius: '4px',
                          overflow: 'hidden',
                        }}
                      >
                        <Box
                          sx={{
                            width: `${percentage}%`,
                            height: '100%',
                            background: `linear-gradient(90deg, ${
                              score >= 4 ? '#43e97b' : score >= 3 ? '#38f9d7' : score >= 2 ? '#ffa726' : '#f44336'
                            }, ${score >= 4 ? '#38f9d7' : score >= 3 ? '#667eea' : score >= 2 ? '#ff7043' : '#e53935'})`,
                            transition: 'width 0.5s ease',
                          }}
                        />
                      </Box>
                    </Box>
                  );
                })}
              </Box>
            </Paper>
          </Grid>

          {/* Strengths */}
          <Grid item xs={12} md={6} className="avoid-break">
            <Paper
              className="print-optimize"
              sx={{
                p: 3,
                background: 'rgba(67, 233, 123, 0.1)',
                backdropFilter: 'blur(20px)',
                borderRadius: '20px',
                border: '1px solid rgba(67, 233, 123, 0.3)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <CheckCircleIcon sx={{ color: '#43e97b', fontSize: 28 }} />
                <Typography variant="h6" sx={{ color: '#43e97b', fontWeight: 700 }}>
                  核心优势
                </Typography>
              </Box>
              <List>
                {evaluation.overall_strengths?.map((strength, idx) => (
                  <ListItem key={idx} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <CheckCircleIcon sx={{ color: '#43e97b', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={strength}
                      primaryTypographyProps={{
                        sx: { color: 'rgba(255, 255, 255, 0.9)', lineHeight: 1.6 },
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Weaknesses */}
          <Grid item xs={12} md={6} className="avoid-break">
            <Paper
              className="print-optimize"
              sx={{
                p: 3,
                background: 'rgba(255, 167, 38, 0.1)',
                backdropFilter: 'blur(20px)',
                borderRadius: '20px',
                border: '1px solid rgba(255, 167, 38, 0.3)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <WarningIcon sx={{ color: '#ffa726', fontSize: 28 }} />
                <Typography variant="h6" sx={{ color: '#ffa726', fontWeight: 700 }}>
                  主要不足
                </Typography>
              </Box>
              <List>
                {evaluation.overall_weaknesses?.map((weakness, idx) => (
                  <ListItem key={idx} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <WarningIcon sx={{ color: '#ffa726', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={weakness}
                      primaryTypographyProps={{
                        sx: { color: 'rgba(255, 255, 255, 0.9)', lineHeight: 1.6 },
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Key Improvements */}
          <Grid item xs={12} className="avoid-break">
            <Paper
              className="print-optimize"
              sx={{
                p: 3,
                background: 'rgba(56, 249, 215, 0.1)',
                backdropFilter: 'blur(20px)',
                borderRadius: '20px',
                border: '1px solid rgba(56, 249, 215, 0.3)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <LightbulbIcon sx={{ color: '#38f9d7', fontSize: 28 }} />
                <Typography variant="h6" sx={{ color: '#38f9d7', fontWeight: 700 }}>
                  关键改进建议
                </Typography>
              </Box>
              <Grid container spacing={2}>
                {evaluation.key_improvements?.map((improvement, idx) => (
                  <Grid item xs={12} md={6} key={idx}>
                    <Card
                      sx={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: '12px',
                        border: '1px solid rgba(56, 249, 215, 0.2)',
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', gap: 1.5 }}>
                          <Typography
                            sx={{
                              color: '#38f9d7',
                              fontWeight: 700,
                              fontSize: '1.25rem',
                            }}
                          >
                            {idx + 1}.
                          </Typography>
                          <Typography sx={{ color: 'rgba(255, 255, 255, 0.9)', lineHeight: 1.6 }}>
                            {improvement}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>

          {/* Uncompleted Tasks */}
          {evaluation.uncompleted_tasks && evaluation.uncompleted_tasks.length > 0 && (
            <Grid item xs={12} className="avoid-break">
              <Paper
                className="print-optimize"
                sx={{
                  p: 3,
                  background: 'rgba(244, 67, 54, 0.1)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '20px',
                  border: '1px solid rgba(244, 67, 54, 0.3)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <WarningIcon sx={{ color: '#f44336', fontSize: 28 }} />
                  <Typography variant="h6" sx={{ color: '#f44336', fontWeight: 700 }}>
                    未完成任务
                  </Typography>
                </Box>
                <List>
                  {evaluation.uncompleted_tasks.map((task, idx) => (
                    <ListItem key={idx} sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <WarningIcon sx={{ color: '#f44336', fontSize: 20 }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={task}
                        primaryTypographyProps={{
                          sx: { color: 'rgba(255, 255, 255, 0.9)', lineHeight: 1.6 },
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          )}

          {/* Stage Details */}
          <Grid item xs={12}>
            <Paper
              className="print-optimize allow-break"
              sx={{
                p: 3,
                background: 'rgba(255, 255, 255, 0.03)',
                backdropFilter: 'blur(20px)',
                borderRadius: '20px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
              }}
            >
              <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700, mb: 2 }}>
                各阶段详细评价
              </Typography>
              {evaluation.stage_details?.map((stage, idx) => (
                <Accordion
                  key={idx}
                  defaultExpanded
                  className="allow-break"
                  sx={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    color: '#fff',
                    mb: 1,
                    '&:before': { display: 'none' },
                    borderRadius: '12px !important',
                  }}
                >
                  <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#fff' }} className="no-print" />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                      <Typography sx={{ fontWeight: 600 }}>
                        阶段 {stage.stage}: {stage.stage_name}
                      </Typography>
                      <Chip
                        label={`${stage.score}/5`}
                        size="small"
                        sx={{
                          background:
                            stage.score >= 4
                              ? '#43e97b'
                              : stage.score >= 3
                              ? '#38f9d7'
                              : stage.score >= 2
                              ? '#ffa726'
                              : '#f44336',
                          color: '#fff',
                          fontWeight: 700,
                        }}
                      />
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', ml: 'auto' }}>
                        用时 {stage.rounds_used} 轮
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" sx={{ color: '#43e97b', mb: 1 }}>
                          优点
                        </Typography>
                        <List dense>
                          {stage.strengths?.map((s, i) => (
                            <ListItem key={i} sx={{ px: 0 }}>
                              <ListItemIcon sx={{ minWidth: 24 }}>
                                <CheckCircleIcon sx={{ color: '#43e97b', fontSize: 16 }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={s}
                                primaryTypographyProps={{
                                  sx: { color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.875rem' },
                                }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" sx={{ color: '#ffa726', mb: 1 }}>
                          不足
                        </Typography>
                        <List dense>
                          {stage.weaknesses?.map((w, i) => (
                            <ListItem key={i} sx={{ px: 0 }}>
                              <ListItemIcon sx={{ minWidth: 24 }}>
                                <WarningIcon sx={{ color: '#ffa726', fontSize: 16 }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={w}
                                primaryTypographyProps={{
                                  sx: { color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.875rem' },
                                }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" sx={{ color: '#38f9d7', mb: 1 }}>
                          建议
                        </Typography>
                        <List dense>
                          {stage.suggestions?.map((sg, i) => (
                            <ListItem key={i} sx={{ px: 0 }}>
                              <ListItemIcon sx={{ minWidth: 24 }}>
                                <LightbulbIcon sx={{ color: '#38f9d7', fontSize: 16 }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={sg}
                                primaryTypographyProps={{
                                  sx: { color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.875rem' },
                                }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
}

export default EvaluationReportPage;
