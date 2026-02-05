import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Grid,
  Chip,
  Divider,
  Alert,
  LinearProgress
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DownloadIcon from '@mui/icons-material/Download';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer
} from 'recharts';

// 深色主题
const theme = {
  bgPrimary: '#0a0e17',
  bgSecondary: '#0d1321',
  bgCard: 'rgba(19, 26, 43, 0.9)',
  primary: '#00d4ff',
  primaryGlow: 'rgba(0, 212, 255, 0.15)',
  accent: '#7c3aed',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  textPrimary: '#f1f5f9',
  textSecondary: '#94a3b8',
  textMuted: '#64748b',
  border: 'rgba(255, 255, 255, 0.08)',
  borderHover: 'rgba(0, 212, 255, 0.3)',
  gradientPrimary: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
};

const InterviewReportPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [rounds, setRounds] = useState([]);
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReportData();
  }, [sessionId]);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      setError(null);

      const sessionRes = await axios.get(`/api/digital-interviewer/sessions/${sessionId}`);
      setSession(sessionRes.data.session);

      const roundsRes = await axios.get(`/api/digital-interviewer/sessions/${sessionId}/rounds`);
      setRounds(roundsRes.data.rounds || []);

      const evalRes = await axios.get(`/api/digital-interviewer/sessions/${sessionId}/evaluation`);
      setEvaluation(evalRes.data.evaluation);

    } catch (err) {
      console.error('获取报告数据失败:', err);
      setError(err.response?.data?.detail || '获取报告数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async () => {
    try {
      const response = await axios.get(
        `/api/digital-interviewer/sessions/${sessionId}/download-pdf`,
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `interview_report_${sessionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('导出PDF失败:', err);
      alert('导出PDF失败: ' + (err.response?.data?.detail || err.message));
    }
  };

  // 样式定义
  const pageStyle = {
    minHeight: '100vh',
    background: `
      radial-gradient(ellipse at 20% 0%, rgba(0, 212, 255, 0.08) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 100%, rgba(124, 58, 237, 0.08) 0%, transparent 50%),
      linear-gradient(180deg, ${theme.bgPrimary} 0%, ${theme.bgSecondary} 100%)
    `,
    py: 4,
  };

  const glassCard = {
    background: theme.bgCard,
    backdropFilter: 'blur(20px)',
    border: `1px solid ${theme.border}`,
    borderRadius: '16px',
    p: 3,
    mb: 3,
  };

  if (loading) {
    return (
      <Box sx={pageStyle}>
        <Container maxWidth="lg" sx={{ textAlign: 'center', pt: 10 }}>
          <CircularProgress sx={{ color: theme.primary }} />
          <Typography sx={{ mt: 2, color: theme.textSecondary }}>加载报告数据...</Typography>
        </Container>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={pageStyle}>
        <Container maxWidth="lg" sx={{ pt: 4 }}>
          <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/digital-interviewer')}
            sx={{ color: theme.primary }}
          >
            返回
          </Button>
        </Container>
      </Box>
    );
  }

  if (!session) {
    return (
      <Box sx={pageStyle}>
        <Container maxWidth="lg" sx={{ pt: 4 }}>
          <Alert severity="warning">报告数据不完整</Alert>
          <Button sx={{ mt: 2, color: theme.primary }} onClick={() => navigate('/digital-interviewer')}>
            返回
          </Button>
        </Container>
      </Box>
    );
  }

  const evalData = evaluation || {
    technical_score: 0,
    communication_score: 0,
    problem_solving_score: 0,
    cultural_fit_score: 0,
    total_score: 0,
    performance_level: '未完成',
    strengths: [],
    weaknesses: [],
    suggestions: []
  };

  const radarData = [
    { subject: '技术能力', score: evalData.technical_score, fullMark: 10 },
    { subject: '沟通能力', score: evalData.communication_score, fullMark: 10 },
    { subject: '问题解决', score: evalData.problem_solving_score, fullMark: 10 },
    { subject: '文化匹配', score: evalData.cultural_fit_score, fullMark: 10 }
  ];

  return (
    <Box sx={pageStyle}>
      <Container maxWidth="lg">
        {/* 返回按钮 */}
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/digital-interviewer')}
          sx={{ mb: 3, color: theme.textSecondary, '&:hover': { color: theme.primary } }}
        >
          返回面试官
        </Button>

        {/* 标题 */}
        <Typography sx={{
          fontSize: '2rem',
          fontWeight: 700,
          background: theme.gradientPrimary,
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          mb: 4,
        }}>
          面试报告
        </Typography>

        {/* 1. 基本信息 */}
        <Box sx={glassCard}>
          <Typography sx={{ color: theme.textPrimary, fontSize: '1.2rem', fontWeight: 600, mb: 2 }}>
            基本信息
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem' }}>候选人</Typography>
              <Typography sx={{ color: theme.textPrimary, fontWeight: 500 }}>
                {session.candidate_name || '未提供'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem' }}>面试官</Typography>
              <Typography sx={{ color: theme.textPrimary, fontWeight: 500 }}>
                {session.interviewer_name}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem' }}>面试类型</Typography>
              <Typography sx={{ color: theme.textPrimary, fontWeight: 500 }}>
                {session.interview_type === 'technical' ? '技术面试' :
                 session.interview_type === 'hr' ? 'HR面试' : '行为面试'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem' }}>面试时间</Typography>
              <Typography sx={{ color: theme.textPrimary, fontWeight: 500 }}>
                {new Date(session.created_at).toLocaleString()}
              </Typography>
            </Grid>
          </Grid>
        </Box>

        {/* 2. 综合评分 */}
        <Box sx={glassCard}>
          <Typography sx={{ color: theme.textPrimary, fontSize: '1.2rem', fontWeight: 600, mb: 3 }}>
            综合评分
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke={theme.border} />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: theme.textSecondary, fontSize: 12 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 10]} tick={{ fill: theme.textMuted }} />
                  <Radar
                    name="评分"
                    dataKey="score"
                    stroke={theme.primary}
                    fill={theme.primary}
                    fillOpacity={0.4}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <Typography sx={{
                    fontSize: '3rem',
                    fontWeight: 700,
                    background: theme.gradientPrimary,
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}>
                    {evalData.total_score}/40
                  </Typography>
                  <Chip
                    label={evalData.performance_level}
                    sx={{
                      mt: 1,
                      background: evalData.performance_level === '优秀' ? 'rgba(16, 185, 129, 0.2)' :
                                  evalData.performance_level === '良好' ? 'rgba(0, 212, 255, 0.2)' :
                                  'rgba(245, 158, 11, 0.2)',
                      color: evalData.performance_level === '优秀' ? theme.success :
                             evalData.performance_level === '良好' ? theme.primary : theme.warning,
                      fontWeight: 600,
                    }}
                  />
                </Box>
                {[
                  { label: '技术能力', value: evalData.technical_score },
                  { label: '沟通能力', value: evalData.communication_score },
                  { label: '问题解决', value: evalData.problem_solving_score },
                  { label: '文化匹配', value: evalData.cultural_fit_score },
                ].map((item, i) => (
                  <Box key={i}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem' }}>{item.label}</Typography>
                      <Typography sx={{ color: theme.primary, fontSize: '0.9rem', fontWeight: 600 }}>{item.value}/10</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={item.value * 10}
                      sx={{
                        height: 6, borderRadius: 3,
                        background: 'rgba(255,255,255,0.1)',
                        '& .MuiLinearProgress-bar': { background: theme.gradientPrimary, borderRadius: 3 },
                      }}
                    />
                  </Box>
                ))}
              </Box>
            </Grid>
          </Grid>
        </Box>

        {/* 3. 评估反馈 */}
        <Box sx={glassCard}>
          <Typography sx={{ color: theme.textPrimary, fontSize: '1.2rem', fontWeight: 600, mb: 3 }}>
            评估反馈
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, borderRadius: '12px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <Typography sx={{ color: theme.success, fontWeight: 600, mb: 1 }}>✓ 优势</Typography>
                {evalData.strengths && evalData.strengths.length > 0 ? (
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    {evalData.strengths.map((s, i) => (
                      <li key={i}><Typography sx={{ color: theme.textPrimary, fontSize: '0.9rem' }}>{s}</Typography></li>
                    ))}
                  </ul>
                ) : (
                  <Typography sx={{ color: theme.textMuted, fontSize: '0.9rem' }}>暂无数据</Typography>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, borderRadius: '12px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                <Typography sx={{ color: theme.warning, fontWeight: 600, mb: 1 }}>⚠ 待改进</Typography>
                {evalData.weaknesses && evalData.weaknesses.length > 0 ? (
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    {evalData.weaknesses.map((w, i) => (
                      <li key={i}><Typography sx={{ color: theme.textPrimary, fontSize: '0.9rem' }}>{w}</Typography></li>
                    ))}
                  </ul>
                ) : (
                  <Typography sx={{ color: theme.textMuted, fontSize: '0.9rem' }}>暂无数据</Typography>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, borderRadius: '12px', background: 'rgba(0, 212, 255, 0.1)', border: '1px solid rgba(0, 212, 255, 0.3)' }}>
                <Typography sx={{ color: theme.primary, fontWeight: 600, mb: 1 }}>💡 建议</Typography>
                {evalData.suggestions && evalData.suggestions.length > 0 ? (
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    {evalData.suggestions.map((s, i) => (
                      <li key={i}><Typography sx={{ color: theme.textPrimary, fontSize: '0.9rem' }}>{s}</Typography></li>
                    ))}
                  </ul>
                ) : (
                  <Typography sx={{ color: theme.textMuted, fontSize: '0.9rem' }}>暂无数据</Typography>
                )}
              </Box>
            </Grid>
          </Grid>
        </Box>

        {/* 4. 面试详情 */}
        <Box sx={glassCard}>
          <Typography sx={{ color: theme.textPrimary, fontSize: '1.2rem', fontWeight: 600, mb: 3 }}>
            面试详情
          </Typography>
          {rounds.length === 0 ? (
            <Typography sx={{ color: theme.textMuted }}>暂无面试轮次数据</Typography>
          ) : (
            rounds.map((round, index) => (
              <Box
                key={round.id}
                sx={{
                  mt: index > 0 ? 3 : 0,
                  p: 3,
                  background: 'rgba(0, 0, 0, 0.2)',
                  borderRadius: '12px',
                  borderLeft: `4px solid ${theme.primary}`,
                }}
              >
                <Typography sx={{ color: theme.primary, fontWeight: 600, fontSize: '1.1rem', mb: 2 }}>
                  第 {index + 1} 轮
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography sx={{ color: theme.textSecondary, fontSize: '0.85rem', mb: 0.5 }}>问题</Typography>
                  <Typography sx={{ color: theme.textPrimary, lineHeight: 1.6 }}>{round.question}</Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography sx={{ color: theme.textSecondary, fontSize: '0.85rem', mb: 0.5 }}>回答</Typography>
                  <Typography sx={{ color: theme.textPrimary, lineHeight: 1.6 }}>{round.answer || '未回答'}</Typography>
                </Box>
                {round.evaluation_data && (
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip
                      label={`技术 ${round.evaluation_data.technical_score || 0}/10`}
                      size="small"
                      sx={{ background: theme.primaryGlow, color: theme.primary, border: `1px solid ${theme.borderHover}` }}
                    />
                    <Chip
                      label={`沟通 ${round.evaluation_data.communication_score || 0}/10`}
                      size="small"
                      sx={{ background: theme.primaryGlow, color: theme.primary, border: `1px solid ${theme.borderHover}` }}
                    />
                    <Chip
                      label={`问题解决 ${round.evaluation_data.problem_solving_score || 0}/10`}
                      size="small"
                      sx={{ background: theme.primaryGlow, color: theme.primary, border: `1px solid ${theme.borderHover}` }}
                    />
                  </Box>
                )}
              </Box>
            ))
          )}
        </Box>

        {/* 5. 导出按钮 */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleExportPDF}
            sx={{
              background: theme.gradientPrimary,
              color: '#fff',
              fontWeight: 600,
              py: 1.5,
              px: 4,
              borderRadius: '12px',
              textTransform: 'none',
              boxShadow: '0 4px 20px rgba(0, 212, 255, 0.3)',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 30px rgba(0, 212, 255, 0.4)',
              },
            }}
          >
            导出PDF报告
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/digital-interviewer')}
            sx={{
              color: theme.textSecondary,
              borderColor: theme.border,
              py: 1.5,
              px: 4,
              borderRadius: '12px',
              textTransform: 'none',
              '&:hover': {
                borderColor: theme.primary,
                color: theme.primary,
              },
            }}
          >
            返回首页
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default InterviewReportPage;
