import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Typography,
  Grid,
  Button,
  Tabs,
  Tab,
  TextField,
  MenuItem,
  CircularProgress,
  Switch,
  FormControlLabel,
  LinearProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  FormGroup,
  Chip,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import PersonIcon from '@mui/icons-material/Person';
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter';
import HistoryIcon from '@mui/icons-material/History';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import VideocamIcon from '@mui/icons-material/Videocam';
import MicIcon from '@mui/icons-material/Mic';
import AssessmentIcon from '@mui/icons-material/Assessment';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';

// 导入组件
import InterviewerCard from '../components/digital_interviewer/InterviewerCard';
import InterviewerUpload from '../components/digital_interviewer/InterviewerUpload';
import DigitalHumanPlayer from '../components/digital_interviewer/DigitalHumanPlayer';
import InterviewChat from '../components/digital_interviewer/InterviewChat';
import InterviewFeedback from '../components/digital_interviewer/InterviewFeedback';
import VoiceInterviewInput from '../components/digital_interviewer/VoiceInterviewInput';

// 导入Hook
import useInterviewWebSocket from '../hooks/useInterviewWebSocket';
import useInterviewerVoice from '../hooks/useInterviewerVoice';

// ==================== 商务科技风格主题 ====================
const theme = {
  bgPrimary: '#0a0e17',
  bgSecondary: '#0d1321',
  bgCard: 'rgba(19, 26, 43, 0.8)',
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
  borderActive: 'rgba(0, 212, 255, 0.6)',
  gradientPrimary: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
};

const DigitalInterviewerPage = () => {
  // Tab状态
  const [activeTab, setActiveTab] = useState('list'); // 'list' | 'training' | 'history' | 'experience'

  // 面试官列表
  const [interviewers, setInterviewers] = useState([]);
  const [loading, setLoading] = useState(true);

  // 面试训练状态
  const [selectedInterviewer, setSelectedInterviewer] = useState(null);
  const [interviewType, setInterviewType] = useState('technical');
  const [candidateName, setCandidateName] = useState('候选人');
  const [sessionId, setSessionId] = useState(null);
  const [isStarting, setIsStarting] = useState(false);

  // 虚拟人形象状态
  const [digitalHumans, setDigitalHumans] = useState([]);
  const [selectedDigitalHuman, setSelectedDigitalHuman] = useState(null);
  const [loadingDigitalHumans, setLoadingDigitalHumans] = useState(false);

  // 面经相关状态
  const [experienceSets, setExperienceSets] = useState([]);
  const [loadingExperience, setLoadingExperience] = useState(false);
  const [selectedExperienceSets, setSelectedExperienceSets] = useState([]);
  const [experienceMode, setExperienceMode] = useState('none'); // none/reference/strict/mixed
  const [maxRounds, setMaxRounds] = useState(5); // 最大面试轮数，默认5轮
  const [uploadingExperience, setUploadingExperience] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({ current: 0, total: 100, message: '', questionsFound: 0 });
  const [experienceUploadForm, setExperienceUploadForm] = useState({
    name: '',
    interview_type: 'technical',
    description: '',
    company: '',
    position: ''
  });
  const [viewQuestionsDialog, setViewQuestionsDialog] = useState({ open: false, questions: [], setName: '' });

  // 面试过程状态
  const [currentVideoState, setCurrentVideoState] = useState('idle');
  const [chatMessages, setChatMessages] = useState([]);
  const [currentEvaluation, setCurrentEvaluation] = useState(null);
  const [interviewEnded, setInterviewEnded] = useState(false);
  const [interviewStarted, setInterviewStarted] = useState(false); // 面试是否已开始
  const [digitalHumanVideos, setDigitalHumanVideos] = useState(null); // 当前使用的虚拟人视频
  const [isInterviewerSpeaking, setIsInterviewerSpeaking] = useState(false); // 面试官是否正在说话
  const [voiceMode, setVoiceMode] = useState(true); // 是否启用语音模式

  // 候选人视频状态
  const [candidateStream, setCandidateStream] = useState(null);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const candidateVideoRef = React.useRef(null);
  const chatContainerRef = useRef(null);
  const processedMsgCountRef = useRef(0); // 跟踪已处理的消息数量，避免重复处理

  // 面试记录
  const [interviewHistory, setInterviewHistory] = useState([]);

  // WebSocket集成
  const { connected, messages, sendMessage } = useInterviewWebSocket(sessionId);

  // TTS语音Hook
  const { speak, preload: preloadVoice, stop: stopSpeaking } = useInterviewerVoice();

  const navigate = useNavigate();

  // 获取面试官列表
  useEffect(() => {
    fetchInterviewers();
    fetchDigitalHumans();
    fetchExperienceSets();
  }, []);

  const fetchInterviewers = async () => {
    try {
      const response = await axios.get('/api/digital-interviewer/interviewers');
      setInterviewers(response.data.interviewers || []);
    } catch (error) {
      console.error('获取面试官列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取面经集列表
  const fetchExperienceSets = async () => {
    setLoadingExperience(true);
    try {
      const response = await axios.get('/api/digital-interviewer/experience-sets');
      setExperienceSets(response.data.experience_sets || []);
    } catch (error) {
      console.error('获取面经集列表失败:', error);
    } finally {
      setLoadingExperience(false);
    }
  };

  // 上传面经（SSE流式）
  const handleUploadExperience = async (file) => {
    if (!file || !experienceUploadForm.name) {
      alert('请填写面经名称并选择文件');
      return;
    }

    setUploadingExperience(true);
    setUploadProgress({ current: 0, total: 100, message: '准备上传...', questionsFound: 0 });

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', experienceUploadForm.name);
      formData.append('interview_type', experienceUploadForm.interview_type);
      formData.append('description', experienceUploadForm.description);
      formData.append('company', experienceUploadForm.company);
      formData.append('position', experienceUploadForm.position);

      // 使用 SSE 流式上传
      const response = await fetch('/api/digital-interviewer/experience-sets/upload-stream', {
        method: 'POST',
        body: formData
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === 'progress') {
                setUploadProgress({
                  current: data.current || 0,
                  total: data.total || 100,
                  message: data.message || '',
                  questionsFound: data.questions_found || 0
                });
              } else if (data.type === 'complete') {
                setUploadProgress({
                  current: data.total,
                  total: data.total,
                  message: data.message,
                  questionsFound: data.result?.questions?.length || 0
                });
              } else if (data.type === 'done') {
                alert(`上传成功！共解析 ${data.experience_set?.question_count || 0} 个问题`);
                fetchExperienceSets();
                setExperienceUploadForm({
                  name: '',
                  interview_type: 'technical',
                  description: '',
                  company: '',
                  position: ''
                });
              } else if (data.type === 'error') {
                alert('上传失败: ' + data.message);
              }
            } catch (e) {
              console.error('解析SSE数据失败:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('上传面经失败:', error);
      alert('上传失败: ' + error.message);
    } finally {
      setUploadingExperience(false);
      setUploadProgress({ current: 0, total: 100, message: '', questionsFound: 0 });
    }
  };

  // 删除面经集
  const handleDeleteExperienceSet = async (setId) => {
    if (!window.confirm('确定要删除这个面经集吗？')) return;

    try {
      await axios.delete(`/api/digital-interviewer/experience-sets/${setId}`);
      fetchExperienceSets();
    } catch (error) {
      console.error('删除面经集失败:', error);
      alert('删除失败');
    }
  };

  // 查看面经问题
  const handleViewQuestions = async (setId, setName) => {
    try {
      const response = await axios.get(`/api/digital-interviewer/experience-sets/${setId}/questions`);
      setViewQuestionsDialog({
        open: true,
        questions: response.data.questions || [],
        setName
      });
    } catch (error) {
      console.error('获取问题失败:', error);
    }
  };

  // 切换面经集选择
  const toggleExperienceSet = (setId) => {
    setSelectedExperienceSets(prev =>
      prev.includes(setId)
        ? prev.filter(id => id !== setId)
        : [...prev, setId]
    );
  };

  // 获取虚拟人形象列表
  const fetchDigitalHumans = async () => {
    setLoadingDigitalHumans(true);
    try {
      const response = await axios.get('/api/digital-interviewer/digital-humans');
      const humanList = response.data.digital_humans || [];
      setDigitalHumans(humanList);

      // 自动选择默认形象
      const defaultHuman = humanList.find(h => h.is_default);
      if (defaultHuman) {
        setSelectedDigitalHuman(defaultHuman);
      } else if (humanList.length > 0) {
        setSelectedDigitalHuman(humanList[0]);
      }
    } catch (error) {
      console.error('获取虚拟人形象列表失败:', error);
      setDigitalHumans([]);
      setSelectedDigitalHuman(null);
    } finally {
      setLoadingDigitalHumans(false);
    }
  };

  // 播放面试官语音（语音就绪后同步显示文字）
  const playInterviewerVoice = useCallback(async (text, playFn) => {
    if (!text) return;

    try {
      setIsInterviewerSpeaking(true);
      setCurrentVideoState('speaking');
      if (playFn) {
        await playFn();
      }
    } catch (err) {
      console.error('TTS播放失败:', err);
    } finally {
      setIsInterviewerSpeaking(false);
      setCurrentVideoState('idle');
    }
  }, []);

  // 处理WebSocket消息
  useEffect(() => {
    // 只处理新消息，避免因依赖项变化导致重复处理
    if (messages.length > processedMsgCountRef.current) {
      // 处理所有新消息
      const newMessages = messages.slice(processedMsgCountRef.current);
      processedMsgCountRef.current = messages.length;

      newMessages.forEach(async (msg) => {
        if (msg.type === 'question') {
          if (voiceMode) {
            // 语音模式：先预加载语音，然后同步显示文字和播放语音
            setCurrentVideoState('thinking'); // 显示思考状态
            const playFn = await preloadVoice(msg.content);

            // 语音就绪后，同时显示文字和播放语音
            setChatMessages(prev => [...prev, {
              role: 'interviewer',
              content: msg.content,
              round: msg.round_number
            }]);

            // 滚动到底部
            setTimeout(() => {
              if (chatContainerRef.current) {
                chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
              }
            }, 100);

            // 播放语音
            playInterviewerVoice(msg.content, playFn);
          } else {
            // 文字模式：直接显示文字
            setChatMessages(prev => [...prev, {
              role: 'interviewer',
              content: msg.content,
              round: msg.round_number
            }]);

            // 滚动到底部
            setTimeout(() => {
              if (chatContainerRef.current) {
                chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
              }
            }, 100);
          }

        } else if (msg.type === 'evaluation') {
          // 收到评估结果
          setCurrentEvaluation(msg.data);
        } else if (msg.type === 'video_state') {
          // 切换视频状态（仅在非语音模式下使用）
          if (!voiceMode) {
            setCurrentVideoState(msg.state);
          }
        } else if (msg.type === 'interview_end') {
          // 面试结束
          setInterviewEnded(true);
          setCurrentVideoState('idle');
          stopSpeaking();
        } else if (msg.type === 'error') {
          // 错误处理
          console.error('WebSocket错误:', msg.message);
        }
      });
    }
  }, [messages]); // 只依赖 messages，其他通过 ref 或闭包访问

  // 开始面试
  const handleStartInterview = async () => {
    if (!selectedInterviewer) {
      alert('请先选择面试官');
      return;
    }

    if (!selectedDigitalHuman) {
      alert('请先选择虚拟人形象');
      return;
    }

    // 验证面经选择
    if (experienceMode !== 'none' && selectedExperienceSets.length === 0) {
      alert('请选择至少一个面经集，或将面经模式设为"不参考"');
      return;
    }

    setIsStarting(true);
    try {
      const formData = new FormData();
      formData.append('interviewer_id', selectedInterviewer.id);
      formData.append('interview_type', interviewType);
      formData.append('candidate_name', candidateName);
      formData.append('digital_human_id', selectedDigitalHuman.id);
      formData.append('experience_set_ids', JSON.stringify(selectedExperienceSets));
      formData.append('experience_mode', experienceMode);
      formData.append('max_rounds', maxRounds);

      const response = await axios.post(
        '/api/digital-interviewer/sessions/start',
        formData
      );

      setSessionId(response.data.session_id);

      // 保存虚拟人形象视频URL
      if (response.data.digital_human_videos) {
        console.log('接收到的视频URL:', response.data.digital_human_videos);
        setDigitalHumanVideos(response.data.digital_human_videos);
      } else {
        console.error('未接收到视频URL');
      }

      setActiveTab('training');
      setChatMessages([]);
      setCurrentEvaluation(null);
      setInterviewEnded(false);
      setInterviewStarted(false); // 重置面试开始状态
      processedMsgCountRef.current = 0; // 重置消息计数器
    } catch (error) {
      console.error('开始面试失败:', error);
      alert('开始面试失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsStarting(false);
    }
  };

  // 发送回答
  const handleSendAnswer = (answer) => {
    if (!answer.trim()) return;

    // 添加到聊天记录
    setChatMessages(prev => [...prev, {
      role: 'candidate',
      content: answer
    }]);

    // 发送到WebSocket
    sendMessage({
      type: 'answer',
      content: answer
    });
  };

  // 开始面试（发送开始信号）
  const handleBeginInterview = () => {
    if (connected) {
      setInterviewStarted(true);
      sendMessage({
        type: 'start_interview',
        experience_set_ids: selectedExperienceSets,
        experience_mode: experienceMode
      });
    }
  };

  // 结束面试
  const handleEndInterview = async () => {
    if (sessionId) {
      try {
        // 发送结束信号
        sendMessage({
          type: 'end_interview'
        });
        setInterviewEnded(true);
        setInterviewStarted(false);
        stopSpeaking();
        setCurrentVideoState('idle');
      } catch (error) {
        console.error('结束面试失败:', error);
      }
    }
  };

  // 查看报告
  const handleViewReport = () => {
    if (sessionId) {
      navigate(`/interview/report/${sessionId}`);
    }
  };

  // 获取面试记录
  const fetchInterviewHistory = async () => {
    try {
      const response = await axios.get('/api/digital-interviewer/sessions');
      setInterviewHistory(response.data.sessions || []);
    } catch (error) {
      console.error('获取面试记录失败:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'history') {
      fetchInterviewHistory();
    }
  }, [activeTab]);

  // 启动候选人摄像头
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false
      });
      setCandidateStream(stream);
      setCameraEnabled(true);
    } catch (err) {
      console.error('无法访问摄像头:', err);
      alert('无法访问摄像头，请检查权限设置');
    }
  };

  // 当candidateStream变化时，设置视频源
  useEffect(() => {
    if (candidateStream && candidateVideoRef.current) {
      candidateVideoRef.current.srcObject = candidateStream;
    }
  }, [candidateStream, cameraEnabled]);

  // 停止候选人摄像头
  const stopCamera = () => {
    if (candidateStream) {
      candidateStream.getTracks().forEach(track => track.stop());
      setCandidateStream(null);
      setCameraEnabled(false);
    }
  };

  // 当进入面试训练时自动启动摄像头
  useEffect(() => {
    if (activeTab === 'training' && sessionId && !cameraEnabled) {
      startCamera();
    }
    return () => {
      if (activeTab !== 'training') {
        stopCamera();
      }
    };
  }, [activeTab, sessionId]);

  // ==================== 样式定义 ====================
  const pageStyle = {
    minHeight: '100vh',
    background: `
      radial-gradient(ellipse at 20% 0%, rgba(0, 212, 255, 0.08) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 100%, rgba(124, 58, 237, 0.08) 0%, transparent 50%),
      linear-gradient(180deg, ${theme.bgPrimary} 0%, ${theme.bgSecondary} 100%)
    `,
    backgroundAttachment: 'fixed',
    position: 'relative',
    p: 4,
  };

  const glassCard = {
    background: theme.bgCard,
    backdropFilter: 'blur(20px)',
    border: `1px solid ${theme.border}`,
    borderRadius: '16px',
    overflow: 'hidden',
    transition: 'all 0.3s ease',
    '&:hover': {
      border: `1px solid ${theme.borderHover}`,
      boxShadow: '0 8px 32px rgba(0, 212, 255, 0.1)',
    },
  };

  const glowCard = {
    ...glassCard,
    border: `1px solid ${theme.borderActive}`,
    boxShadow: '0 0 20px rgba(0, 212, 255, 0.15)',
  };

  const inputStyle = {
    '& .MuiOutlinedInput-root': {
      background: 'rgba(255, 255, 255, 0.03)',
      borderRadius: '10px',
      color: theme.textPrimary,
      '& fieldset': { borderColor: theme.border },
      '&:hover fieldset': { borderColor: theme.borderHover },
      '&.Mui-focused fieldset': { borderColor: theme.primary, borderWidth: '1px' },
    },
    '& .MuiInputLabel-root': { color: theme.textSecondary },
    '& .MuiInputLabel-root.Mui-focused': { color: theme.primary },
    '& .MuiSelect-icon': { color: theme.textSecondary },
  };

  // 下拉菜单样式
  const selectMenuProps = {
    PaperProps: {
      sx: {
        background: theme.bgCard,
        backdropFilter: 'blur(20px)',
        border: `1px solid ${theme.border}`,
        borderRadius: '10px',
        mt: 1,
        '& .MuiMenuItem-root': {
          color: theme.textPrimary,
          '&:hover': {
            background: theme.primaryGlow,
          },
          '&.Mui-selected': {
            background: 'rgba(0, 212, 255, 0.2)',
            '&:hover': {
              background: 'rgba(0, 212, 255, 0.3)',
            },
          },
        },
      },
    },
  };

  const primaryBtn = {
    background: theme.gradientPrimary,
    color: '#fff',
    fontWeight: 600,
    py: 1.5,
    px: 4,
    borderRadius: '12px',
    textTransform: 'none',
    fontSize: '15px',
    boxShadow: '0 4px 20px rgba(0, 212, 255, 0.3)',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 8px 30px rgba(0, 212, 255, 0.4)',
    },
    '&:disabled': {
      background: theme.textMuted,
      boxShadow: 'none',
    },
  };

  return (
    <Box sx={pageStyle}>
      {/* 网格背景 */}
      <Box sx={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        backgroundImage: 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)',
        backgroundSize: '50px 50px',
        pointerEvents: 'none',
        zIndex: 0,
      }} />

      <Box sx={{ position: 'relative', zIndex: 1, maxWidth: '1600px', mx: 'auto' }}>
        {/* 标题区域 */}
        <Box sx={{ mb: 5, textAlign: 'center' }}>
          <Typography sx={{
            fontSize: '2.8rem',
            fontWeight: 700,
            background: theme.gradientPrimary,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-1px',
            mb: 1,
          }}>
            AI 数字面试官
          </Typography>
          <Typography sx={{ color: theme.textSecondary, fontSize: '1.1rem', letterSpacing: '2px' }}>
            INTELLIGENT INTERVIEW TRAINING SYSTEM
          </Typography>
        </Box>

        {/* Tab切换 */}
        <Box sx={{
          borderBottom: `1px solid ${theme.border}`,
          mb: 4,
          '& .MuiTab-root': {
            color: theme.textSecondary,
            textTransform: 'none',
            fontSize: '15px',
            fontWeight: 500,
            minHeight: '56px',
            gap: 1,
            '&:hover': { color: theme.textPrimary },
            '&.Mui-selected': { color: theme.primary },
          },
          '& .MuiTabs-indicator': {
            background: theme.gradientPrimary,
            height: '3px',
            borderRadius: '3px 3px 0 0',
          },
        }}>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
            <Tab icon={<PersonIcon />} iconPosition="start" label="面试官管理" value="list" />
            <Tab icon={<MenuBookIcon />} iconPosition="start" label="面经库" value="experience" />
            <Tab icon={<BusinessCenterIcon />} iconPosition="start" label="面试训练" value="training" />
            <Tab icon={<HistoryIcon />} iconPosition="start" label="面试记录" value="history" />
          </Tabs>
        </Box>

        {/* Tab 1: 面试官管理 */}
        {activeTab === 'list' && (
          <Box sx={{ animation: 'fadeIn 0.5s ease' }}>
            {/* 上传区域 */}
            <Box sx={{ ...glassCard, p: 3, mb: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <CloudUploadIcon sx={{ color: theme.primary, fontSize: 28 }} />
                <Typography sx={{ color: theme.textPrimary, fontSize: '1.1rem', fontWeight: 600 }}>
                  上传面试官画像
                </Typography>
              </Box>
              <InterviewerUpload onUploadSuccess={fetchInterviewers} />
            </Box>

            {/* 面试官列表 */}
            <Typography sx={{ color: theme.textPrimary, fontSize: '1.2rem', fontWeight: 600, mb: 3 }}>
              面试官列表
            </Typography>
            <Grid container spacing={3}>
              {loading ? (
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                    <CircularProgress sx={{ color: theme.primary }} />
                  </Box>
                </Grid>
              ) : interviewers.length === 0 ? (
                <Grid item xs={12}>
                  <Box sx={{ ...glassCard, p: 4, textAlign: 'center' }}>
                    <Typography sx={{ color: theme.textSecondary }}>
                      暂无面试官，请先上传面试官画像
                    </Typography>
                  </Box>
                </Grid>
              ) : (
                interviewers.map((interviewer) => (
                  <Grid item xs={12} sm={6} md={4} key={interviewer.id}>
                    <Box
                      onClick={() => setSelectedInterviewer(interviewer)}
                      sx={{
                        ...(selectedInterviewer?.id === interviewer.id ? glowCard : glassCard),
                        p: 3,
                        cursor: 'pointer',
                        position: 'relative',
                      }}
                    >
                      {selectedInterviewer?.id === interviewer.id && (
                        <Box sx={{
                          position: 'absolute', top: 0, left: 0, right: 0, height: '3px',
                          background: theme.gradientPrimary,
                        }} />
                      )}
                      <Typography sx={{ color: theme.textPrimary, fontWeight: 600, fontSize: '1.1rem', mb: 1 }}>
                        {interviewer.name}
                      </Typography>
                      <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem', mb: 0.5 }}>
                        {interviewer.title}
                      </Typography>
                      <Typography sx={{ color: theme.textMuted, fontSize: '0.85rem' }}>
                        {interviewer.company}
                      </Typography>
                      {interviewer.expertise_areas && (() => {
                        // 解析 expertise_areas，可能是字符串或数组
                        let areas = interviewer.expertise_areas;
                        if (typeof areas === 'string') {
                          try {
                            areas = JSON.parse(areas);
                          } catch {
                            areas = [];
                          }
                        }
                        if (!Array.isArray(areas)) areas = [];
                        return areas.length > 0 ? (
                          <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {areas.slice(0, 3).map((area, i) => (
                              <Box key={i} sx={{
                                px: 1.5, py: 0.5, borderRadius: '20px', fontSize: '0.75rem',
                                background: theme.primaryGlow, color: theme.primary,
                                border: `1px solid ${theme.borderHover}`,
                              }}>
                                {area}
                              </Box>
                            ))}
                          </Box>
                        ) : null;
                      })()}
                    </Box>
                  </Grid>
                ))
              )}
            </Grid>

            {/* 开始面试配置 */}
            {selectedInterviewer && (
              <Box sx={{ ...glowCard, p: 4, mt: 4 }}>
                <Box sx={{
                  position: 'absolute', top: 0, left: 0, right: 0, height: '3px',
                  background: theme.gradientPrimary,
                }} />
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <PlayArrowIcon sx={{ color: theme.primary, fontSize: 28 }} />
                  <Typography sx={{ color: theme.textPrimary, fontSize: '1.2rem', fontWeight: 600 }}>
                    开始面试
                  </Typography>
                </Box>
                <Grid container spacing={3} alignItems="center">
                  <Grid item xs={12} sm={6} md={3}>
                    <TextField
                      fullWidth
                      label="候选人姓名"
                      value={candidateName}
                      onChange={(e) => setCandidateName(e.target.value)}
                      sx={inputStyle}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <TextField
                      fullWidth
                      select
                      label="虚拟人形象"
                      value={selectedDigitalHuman?.id || ''}
                      onChange={(e) => {
                        const human = digitalHumans.find(h => h.id === parseInt(e.target.value));
                        setSelectedDigitalHuman(human);
                      }}
                      disabled={loadingDigitalHumans || digitalHumans.length === 0}
                      sx={inputStyle}
                      SelectProps={{ MenuProps: selectMenuProps }}
                    >
                      {digitalHumans.length === 0 ? (
                        <MenuItem value="">无可用形象</MenuItem>
                      ) : (
                        digitalHumans.map((human) => (
                          <MenuItem key={human.id} value={human.id}>
                            {human.display_name} {human.is_default ? '(默认)' : ''}
                          </MenuItem>
                        ))
                      )}
                    </TextField>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <TextField
                      fullWidth
                      select
                      label="面试类型"
                      value={interviewType}
                      onChange={(e) => setInterviewType(e.target.value)}
                      sx={inputStyle}
                      SelectProps={{ MenuProps: selectMenuProps }}
                    >
                      <MenuItem value="technical">技术面试</MenuItem>
                      <MenuItem value="hr">HR面试</MenuItem>
                      <MenuItem value="behavioral">行为面试</MenuItem>
                    </TextField>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      fullWidth
                      onClick={handleStartInterview}
                      disabled={isStarting || !selectedDigitalHuman}
                      sx={primaryBtn}
                    >
                      {isStarting ? (
                        <CircularProgress size={24} sx={{ color: '#fff' }} />
                      ) : (
                        '开始面试'
                      )}
                    </Button>
                  </Grid>
                </Grid>

                {/* 面经选择区域 */}
                <Box sx={{ mt: 3, pt: 3, borderTop: `1px solid ${theme.border}` }}>
                  <Typography sx={{ color: theme.textPrimary, fontWeight: 600, mb: 2 }}>
                    面经配置（可选）
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        fullWidth
                        select
                        label="面经使用模式"
                        value={experienceMode}
                        onChange={(e) => setExperienceMode(e.target.value)}
                        sx={inputStyle}
                        SelectProps={{ MenuProps: selectMenuProps }}
                      >
                        <MenuItem value="none">不参考面经</MenuItem>
                        <MenuItem value="reference">参考模式（AI可改编）</MenuItem>
                        <MenuItem value="strict">严格模式（使用原题）</MenuItem>
                        <MenuItem value="mixed">混合模式（首轮原题+追问）</MenuItem>
                      </TextField>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        fullWidth
                        select
                        label="面试轮数"
                        value={maxRounds}
                        onChange={(e) => setMaxRounds(Number(e.target.value))}
                        sx={inputStyle}
                        SelectProps={{ MenuProps: selectMenuProps }}
                      >
                        <MenuItem value={3}>3 轮</MenuItem>
                        <MenuItem value={5}>5 轮（默认）</MenuItem>
                        <MenuItem value={8}>8 轮</MenuItem>
                        <MenuItem value={10}>10 轮</MenuItem>
                      </TextField>
                    </Grid>
                    {experienceMode !== 'none' && (
                      <Grid item xs={12} sm={6} md={8}>
                        <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem', mb: 1 }}>
                          选择面经集
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {experienceSets.length === 0 ? (
                            <Typography sx={{ color: theme.textMuted, fontSize: '0.85rem' }}>
                              暂无面经，请先在"面经库"页面上传
                            </Typography>
                          ) : (
                            experienceSets.map(set => (
                              <Chip
                                key={set.id}
                                label={`${set.name} (${set.question_count}题)`}
                                onClick={() => toggleExperienceSet(set.id)}
                                sx={{
                                  background: selectedExperienceSets.includes(set.id)
                                    ? 'rgba(0, 212, 255, 0.2)'
                                    : 'rgba(255, 255, 255, 0.05)',
                                  color: selectedExperienceSets.includes(set.id)
                                    ? theme.primary
                                    : theme.textSecondary,
                                  border: `1px solid ${selectedExperienceSets.includes(set.id)
                                    ? theme.borderActive
                                    : theme.border}`,
                                  '&:hover': {
                                    background: 'rgba(0, 212, 255, 0.15)',
                                  },
                                }}
                              />
                            ))
                          )}
                        </Box>
                      </Grid>
                    )}
                  </Grid>
                </Box>

                {digitalHumans.length === 0 && !loadingDigitalHumans && (
                  <Box sx={{
                    mt: 3, p: 2, borderRadius: '10px',
                    background: 'rgba(245, 158, 11, 0.1)',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                  }}>
                    <Typography sx={{ color: theme.warning, fontSize: '0.9rem' }}>
                      暂无可用的虚拟人形象。请将视频文件放到 backend/data/digital_humans/ 目录下，然后重启后端。
                    </Typography>
                  </Box>
                )}
              </Box>
            )}
          </Box>
        )}

        {/* Tab 2: 面经库 */}
        {activeTab === 'experience' && (
          <Box sx={{ animation: 'fadeIn 0.5s ease' }}>
            {/* 上传区域 */}
            <Box sx={{ ...glassCard, p: 3, mb: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <CloudUploadIcon sx={{ color: theme.primary, fontSize: 28 }} />
                <Typography sx={{ color: theme.textPrimary, fontSize: '1.1rem', fontWeight: 600 }}>
                  上传面经PDF
                </Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <TextField
                    fullWidth
                    label="面经名称"
                    value={experienceUploadForm.name}
                    onChange={(e) => setExperienceUploadForm(prev => ({ ...prev, name: e.target.value }))}
                    sx={inputStyle}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    select
                    label="面试类型"
                    value={experienceUploadForm.interview_type}
                    onChange={(e) => setExperienceUploadForm(prev => ({ ...prev, interview_type: e.target.value }))}
                    sx={inputStyle}
                    SelectProps={{ MenuProps: selectMenuProps }}
                  >
                    <MenuItem value="technical">技术面试</MenuItem>
                    <MenuItem value="hr">HR面试</MenuItem>
                    <MenuItem value="behavioral">行为面试</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label="目标公司"
                    value={experienceUploadForm.company}
                    onChange={(e) => setExperienceUploadForm(prev => ({ ...prev, company: e.target.value }))}
                    sx={inputStyle}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label="目标职位"
                    value={experienceUploadForm.position}
                    onChange={(e) => setExperienceUploadForm(prev => ({ ...prev, position: e.target.value }))}
                    sx={inputStyle}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    component="label"
                    fullWidth
                    disabled={uploadingExperience || !experienceUploadForm.name}
                    sx={{
                      ...primaryBtn,
                      height: '56px',
                    }}
                  >
                    {uploadingExperience ? (
                      <CircularProgress size={24} sx={{ color: '#fff' }} />
                    ) : (
                      <>
                        <CloudUploadIcon sx={{ mr: 1 }} />
                        选择PDF文件
                      </>
                    )}
                    <input
                      type="file"
                      accept=".pdf"
                      hidden
                      onChange={(e) => {
                        if (e.target.files[0]) {
                          handleUploadExperience(e.target.files[0]);
                        }
                      }}
                    />
                  </Button>
                </Grid>
              </Grid>

              {/* 上传进度条 */}
              {uploadingExperience && (
                <Box sx={{ mt: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem' }}>
                      {uploadProgress.message}
                    </Typography>
                    <Typography sx={{ color: theme.primary, fontSize: '0.9rem', fontWeight: 600 }}>
                      {uploadProgress.total > 0 ? Math.round((uploadProgress.current / uploadProgress.total) * 100) : 0}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={uploadProgress.total > 0 ? (uploadProgress.current / uploadProgress.total) * 100 : 0}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      background: 'rgba(255,255,255,0.1)',
                      '& .MuiLinearProgress-bar': {
                        background: theme.gradientPrimary,
                        borderRadius: 4,
                      },
                    }}
                  />
                  {uploadProgress.questionsFound > 0 && (
                    <Typography sx={{ color: theme.success, fontSize: '0.85rem', mt: 1 }}>
                      已发现 {uploadProgress.questionsFound} 个问题
                    </Typography>
                  )}
                </Box>
              )}
            </Box>

            {/* 面经集列表 */}
            <Typography sx={{ color: theme.textPrimary, fontSize: '1.2rem', fontWeight: 600, mb: 3 }}>
              面经集列表
            </Typography>
            {loadingExperience ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                <CircularProgress sx={{ color: theme.primary }} />
              </Box>
            ) : experienceSets.length === 0 ? (
              <Box sx={{ ...glassCard, p: 4, textAlign: 'center' }}>
                <Typography sx={{ color: theme.textSecondary }}>
                  暂无面经，请上传PDF面经文件
                </Typography>
              </Box>
            ) : (
              <Grid container spacing={3}>
                {experienceSets.map((set) => (
                  <Grid item xs={12} sm={6} md={4} key={set.id}>
                    <Box sx={{ ...glassCard, p: 3 }}>
                      <Typography sx={{ color: theme.textPrimary, fontWeight: 600, fontSize: '1.1rem', mb: 1 }}>
                        {set.name}
                      </Typography>
                      <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem', mb: 0.5 }}>
                        问题数量: {set.question_count}
                      </Typography>
                      {set.company && (
                        <Typography sx={{ color: theme.textMuted, fontSize: '0.85rem' }}>
                          公司: {set.company}
                        </Typography>
                      )}
                      {set.position && (
                        <Typography sx={{ color: theme.textMuted, fontSize: '0.85rem' }}>
                          职位: {set.position}
                        </Typography>
                      )}
                      <Typography sx={{ color: theme.textMuted, fontSize: '0.85rem' }}>
                        来源: {set.source_filename}
                      </Typography>
                      <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                        <Chip
                          size="small"
                          label={set.interview_type === 'technical' ? '技术面试' :
                                 set.interview_type === 'hr' ? 'HR面试' : '行为面试'}
                          sx={{
                            background: theme.primaryGlow,
                            color: theme.primary,
                            border: `1px solid ${theme.borderHover}`,
                          }}
                        />
                      </Box>
                      <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          onClick={() => handleViewQuestions(set.id, set.name)}
                          sx={{
                            color: theme.primary,
                            border: `1px solid ${theme.borderHover}`,
                            '&:hover': { background: theme.primaryGlow },
                          }}
                        >
                          <VisibilityIcon sx={{ fontSize: 18, mr: 0.5 }} />
                          查看问题
                        </Button>
                        <Button
                          size="small"
                          onClick={() => handleDeleteExperienceSet(set.id)}
                          sx={{
                            color: theme.error,
                            border: `1px solid rgba(239, 68, 68, 0.3)`,
                            '&:hover': { background: 'rgba(239, 68, 68, 0.1)' },
                          }}
                        >
                          <DeleteIcon sx={{ fontSize: 18, mr: 0.5 }} />
                          删除
                        </Button>
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        )}

        {/* Tab 3: 面试训练 */}
        {activeTab === 'training' && (
          <Box sx={{ animation: 'fadeIn 0.5s ease' }}>
            {!sessionId ? (
              <Box sx={{ ...glassCard, p: 4, textAlign: 'center' }}>
                <Typography sx={{ color: theme.textSecondary }}>
                  请先在"面试官管理"页面选择面试官并开始面试
                </Typography>
              </Box>
            ) : (
              <Grid container spacing={3}>
                {/* 左栏：数字人视频 */}
                <Grid item xs={12} md={3}>
                  <Box sx={{ ...glassCard, p: 3, height: '620px', display: 'flex', flexDirection: 'column' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <VideocamIcon sx={{ color: theme.primary }} />
                      <Typography sx={{ color: theme.textPrimary, fontWeight: 600 }}>
                        {selectedInterviewer?.name}
                      </Typography>
                    </Box>
                    <Box sx={{
                      flex: 1, minHeight: 0, borderRadius: '12px', overflow: 'hidden',
                      border: `1px solid ${theme.border}`,
                    }}>
                      <DigitalHumanPlayer
                        videoUrls={digitalHumanVideos}
                        currentState={currentVideoState}
                      />
                    </Box>
                    <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {/* 连接状态 */}
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{
                          width: 8, height: 8, borderRadius: '50%',
                          background: connected ? theme.success : theme.error,
                          boxShadow: connected ? '0 0 10px rgba(16, 185, 129, 0.5)' : '0 0 10px rgba(239, 68, 68, 0.5)',
                        }} />
                        <Typography sx={{ color: connected ? theme.success : theme.error, fontSize: '0.85rem' }}>
                          {connected ? '已连接' : '未连接'}
                        </Typography>
                      </Box>
                      {/* 视频状态 */}
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{
                          width: 8, height: 8, borderRadius: '50%',
                          background: currentVideoState === 'idle' ? theme.textMuted : theme.success,
                          animation: currentVideoState !== 'idle' ? 'pulse 1s infinite' : 'none',
                        }} />
                        <Typography
                          sx={{
                            color: currentVideoState === 'idle' ? theme.textMuted : theme.success,
                            fontSize: '0.8rem',
                            fontFamily: 'monospace',
                            letterSpacing: '0.5px',
                          }}
                          className={currentVideoState !== 'idle' ? 'status-text-animate' : ''}
                        >
                          状态: {currentVideoState === 'idle' ? '空闲' :
                                 currentVideoState === 'speaking' ? '说话中' :
                                 currentVideoState === 'listening' ? '聆听中' :
                                 currentVideoState === 'thinking' ? '思考中' : currentVideoState}
                          {currentVideoState !== 'idle' && <span className="dots-animate"></span>}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Grid>

                {/* 中栏：对话区域 */}
                <Grid item xs={12} md={6}>
                  <Box sx={{ ...glassCard, p: 3, height: '620px', display: 'flex', flexDirection: 'column' }}>
                    <Typography sx={{ color: theme.textPrimary, fontWeight: 600, mb: 2 }}>
                      面试对话
                    </Typography>

                    {/* 对话记录 */}
                    <Box
                      ref={chatContainerRef}
                      sx={{
                        flex: 1, overflow: 'auto', mb: 2, p: 2,
                        background: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '12px',
                        border: `1px solid ${theme.border}`,
                      }}
                    >
                      {!interviewStarted ? (
                        <Box sx={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          height: '100%',
                          gap: 3
                        }}>
                          <Typography sx={{ color: theme.textSecondary, textAlign: 'center' }}>
                            {connected ? '准备就绪，点击下方按钮开始面试' : '正在连接...'}
                          </Typography>
                          <Button
                            onClick={handleBeginInterview}
                            disabled={!connected || interviewEnded}
                            sx={{
                              ...primaryBtn,
                              px: 6,
                              py: 2,
                              fontSize: '1.1rem',
                            }}
                          >
                            <PlayArrowIcon sx={{ mr: 1 }} />
                            开始面试
                          </Button>
                        </Box>
                      ) : chatMessages.length === 0 ? (
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                          <Typography sx={{ color: theme.textSecondary }}>
                            等待面试官提问...
                          </Typography>
                        </Box>
                      ) : (
                        chatMessages.map((msg, index) => (
                          <Box
                            key={index}
                            sx={{
                              p: 2, mb: 2, maxWidth: '85%',
                              ml: msg.role === 'interviewer' ? 0 : 'auto',
                              mr: msg.role === 'interviewer' ? 'auto' : 0,
                              background: msg.role === 'interviewer'
                                ? 'rgba(0, 212, 255, 0.1)'
                                : 'rgba(124, 58, 237, 0.1)',
                              border: `1px solid ${msg.role === 'interviewer'
                                ? 'rgba(0, 212, 255, 0.2)'
                                : 'rgba(124, 58, 237, 0.2)'}`,
                              borderRadius: msg.role === 'interviewer'
                                ? '16px 16px 16px 4px'
                                : '16px 16px 4px 16px',
                            }}
                          >
                            <Typography sx={{
                              color: msg.role === 'interviewer' ? theme.primary : theme.accent,
                              fontSize: '0.75rem', fontWeight: 600, mb: 0.5,
                            }}>
                              {msg.role === 'interviewer' ? `面试官 · 第${msg.round}轮` : '我的回答'}
                            </Typography>
                            <Typography sx={{ color: theme.textPrimary, fontSize: '0.95rem', lineHeight: 1.6 }}>
                              {msg.content}
                            </Typography>
                          </Box>
                        ))
                      )}
                    </Box>

                    {/* 输入区域 */}
                    {!interviewEnded && interviewStarted ? (
                      <Box>
                        {/* 语音/文字模式切换 + 结束面试按钮 */}
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                          <Button
                            onClick={handleEndInterview}
                            sx={{
                              color: theme.error,
                              borderColor: theme.error,
                              border: '1px solid',
                              borderRadius: '8px',
                              textTransform: 'none',
                              px: 2,
                              py: 0.5,
                              fontSize: '0.85rem',
                              '&:hover': {
                                background: 'rgba(239, 68, 68, 0.1)',
                                borderColor: theme.error,
                              },
                            }}
                          >
                            <StopIcon sx={{ fontSize: 18, mr: 0.5 }} />
                            结束面试
                          </Button>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={voiceMode}
                                onChange={(e) => setVoiceMode(e.target.checked)}
                                size="small"
                                sx={{
                                  '& .MuiSwitch-switchBase.Mui-checked': { color: theme.primary },
                                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: theme.primary },
                                }}
                              />
                            }
                            label={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <MicIcon sx={{ fontSize: 18, color: voiceMode ? theme.primary : theme.textMuted }} />
                                <Typography sx={{ color: theme.textSecondary, fontSize: '0.85rem' }}>
                                  {voiceMode ? '语音模式' : '文字模式'}
                                </Typography>
                              </Box>
                            }
                          />
                        </Box>

                        {voiceMode ? (
                          <VoiceInterviewInput
                            onAnswerComplete={handleSendAnswer}
                            disabled={interviewEnded || !connected}
                            isInterviewerSpeaking={isInterviewerSpeaking}
                          />
                        ) : (
                          <InterviewChat
                            messages={[]}
                            onSendMessage={handleSendAnswer}
                            disabled={interviewEnded || !connected || isInterviewerSpeaking}
                          />
                        )}
                      </Box>
                    ) : interviewEnded ? (
                      <Box sx={{ textAlign: 'center', py: 2 }}>
                        <Box sx={{
                          p: 2, mb: 2, borderRadius: '10px',
                          background: 'rgba(16, 185, 129, 0.1)',
                          border: '1px solid rgba(16, 185, 129, 0.3)',
                        }}>
                          <Typography sx={{ color: theme.success }}>面试已结束！</Typography>
                        </Box>
                        <Button onClick={handleViewReport} sx={primaryBtn}>
                          查看面试报告
                        </Button>
                      </Box>
                    ) : null}
                  </Box>
                </Grid>

                {/* 右栏：候选人视频 + 实时评估 */}
                <Grid item xs={12} md={3}>
                  <Box sx={{ ...glassCard, p: 3, height: '300px', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <VideocamIcon sx={{ color: theme.accent }} />
                      <Typography sx={{ color: theme.textPrimary, fontWeight: 600 }}>我的视频</Typography>
                    </Box>
                    <Box sx={{
                      height: '200px', borderRadius: '12px', overflow: 'hidden',
                      background: '#000', border: `1px solid ${theme.border}`,
                    }}>
                      {cameraEnabled ? (
                        <video
                          ref={candidateVideoRef}
                          autoPlay playsInline muted
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                      ) : (
                        <Box sx={{
                          width: '100%', height: '100%',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}>
                          <Button onClick={startCamera} sx={{
                            color: theme.primary, border: `1px solid ${theme.borderHover}`,
                            '&:hover': { background: theme.primaryGlow },
                          }}>
                            启动摄像头
                          </Button>
                        </Box>
                      )}
                    </Box>
                  </Box>

                  <Box sx={{ ...glassCard, p: 3, height: '300px', overflow: 'auto' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <AssessmentIcon sx={{ color: theme.primary }} />
                      <Typography sx={{ color: theme.textPrimary, fontWeight: 600 }}>实时评估</Typography>
                    </Box>
                    {currentEvaluation ? (
                      <Box>
                        {[
                          { label: '专业能力', value: currentEvaluation.technical_score || 0 },
                          { label: '沟通表达', value: currentEvaluation.communication_score || 0 },
                          { label: '问题解决', value: currentEvaluation.problem_solving_score || 0 },
                          { label: '文化匹配', value: currentEvaluation.cultural_fit_score || 0 },
                        ].map((item, i) => (
                          <Box key={i} sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                              <Typography sx={{ color: theme.textSecondary, fontSize: '0.85rem' }}>{item.label}</Typography>
                              <Typography sx={{ color: theme.primary, fontSize: '0.85rem', fontWeight: 600 }}>{item.value}/10</Typography>
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
                        <Box sx={{
                          mt: 2, p: 1.5, borderRadius: '8px',
                          background: 'rgba(0, 212, 255, 0.1)',
                          border: `1px solid ${theme.borderHover}`,
                        }}>
                          <Typography sx={{ color: theme.textSecondary, fontSize: '0.8rem' }}>整体质量</Typography>
                          <Typography sx={{ color: theme.primary, fontWeight: 600 }}>{currentEvaluation.quality || '待评估'}</Typography>
                        </Box>
                      </Box>
                    ) : (
                      <Typography sx={{ color: theme.textMuted, fontSize: '0.9rem' }}>
                        回答问题后将显示评估结果
                      </Typography>
                    )}
                  </Box>
                </Grid>
              </Grid>
            )}
          </Box>
        )}

        {/* Tab 3: 面试记录 */}
        {activeTab === 'history' && (
          <Box sx={{ animation: 'fadeIn 0.5s ease' }}>
            <Typography sx={{ color: theme.textPrimary, fontSize: '1.2rem', fontWeight: 600, mb: 3 }}>
              面试记录
            </Typography>
            {interviewHistory.length === 0 ? (
              <Box sx={{ ...glassCard, p: 4, textAlign: 'center' }}>
                <Typography sx={{ color: theme.textSecondary }}>暂无面试记录</Typography>
              </Box>
            ) : (
              <Grid container spacing={2}>
                {interviewHistory.map((session, index) => (
                  <Grid item xs={12} key={session.id}>
                    <Box
                      onClick={() => navigate(`/interview/report/${session.session_id}`)}
                      sx={{
                        ...glassCard,
                        p: 3,
                        cursor: 'pointer',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        animation: `fadeIn 0.5s ease ${index * 0.1}s both`,
                      }}
                    >
                      <Box>
                        <Typography sx={{ color: theme.textPrimary, fontWeight: 600, fontSize: '1.1rem', mb: 0.5 }}>
                          {session.candidate_name}
                        </Typography>
                        <Typography sx={{ color: theme.textSecondary, fontSize: '0.9rem' }}>
                          面试官: {session.interviewer_name} · {session.interview_type === 'technical' ? '技术面试' : session.interview_type === 'hr' ? 'HR面试' : '行为面试'}
                        </Typography>
                        <Typography sx={{ color: theme.textMuted, fontSize: '0.85rem', mt: 0.5 }}>
                          {new Date(session.created_at).toLocaleString()}
                        </Typography>
                      </Box>
                      <Box sx={{
                        px: 2, py: 1, borderRadius: '20px',
                        background: session.status === 'completed' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                        color: session.status === 'completed' ? theme.success : theme.warning,
                        fontSize: '0.85rem', fontWeight: 500,
                      }}>
                        {session.status === 'completed' ? '已完成' : '进行中'}
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        )}
      </Box>

      {/* 全局动画样式 */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.2); }
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        @keyframes dots {
          0% { content: ''; }
          25% { content: '.'; }
          50% { content: '..'; }
          75% { content: '...'; }
          100% { content: ''; }
        }
        .status-text-animate {
          animation: blink 1.5s ease-in-out infinite;
        }
        .dots-animate::after {
          content: '';
          animation: dots 1.5s steps(4, end) infinite;
        }
      `}</style>

      {/* 查看问题对话框 */}
      <Dialog
        open={viewQuestionsDialog.open}
        onClose={() => setViewQuestionsDialog({ open: false, questions: [], setName: '' })}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: theme.bgCard,
            backdropFilter: 'blur(20px)',
            border: `1px solid ${theme.border}`,
            borderRadius: '16px',
          }
        }}
      >
        <DialogTitle sx={{ color: theme.textPrimary, borderBottom: `1px solid ${theme.border}` }}>
          {viewQuestionsDialog.setName} - 问题列表
        </DialogTitle>
        <DialogContent sx={{ mt: 2 }}>
          {viewQuestionsDialog.questions.length === 0 ? (
            <Typography sx={{ color: theme.textSecondary, py: 4, textAlign: 'center' }}>
              暂无问题
            </Typography>
          ) : (
            viewQuestionsDialog.questions.map((q, index) => (
              <Box
                key={q.id || index}
                sx={{
                  p: 2, mb: 2, borderRadius: '10px',
                  background: 'rgba(0, 0, 0, 0.2)',
                  border: `1px solid ${theme.border}`,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Typography sx={{
                    color: theme.primary, fontWeight: 600, fontSize: '0.9rem',
                    background: theme.primaryGlow,
                    px: 1.5, py: 0.5, borderRadius: '12px',
                  }}>
                    Q{index + 1}
                  </Typography>
                  {q.category && (
                    <Chip
                      size="small"
                      label={q.category}
                      sx={{
                        background: 'rgba(124, 58, 237, 0.15)',
                        color: theme.accent,
                        fontSize: '0.75rem',
                      }}
                    />
                  )}
                  {q.difficulty_level && (
                    <Chip
                      size="small"
                      label={q.difficulty_level}
                      sx={{
                        background: q.difficulty_level === 'hard' ? 'rgba(239, 68, 68, 0.15)' :
                                   q.difficulty_level === 'medium' ? 'rgba(245, 158, 11, 0.15)' :
                                   'rgba(16, 185, 129, 0.15)',
                        color: q.difficulty_level === 'hard' ? theme.error :
                               q.difficulty_level === 'medium' ? theme.warning :
                               theme.success,
                        fontSize: '0.75rem',
                      }}
                    />
                  )}
                </Box>
                <Typography sx={{ color: theme.textPrimary, fontSize: '0.95rem', mb: 1 }}>
                  {q.question_text || q.content}
                </Typography>
                {q.reference_answer && (
                  <Box sx={{
                    mt: 1, p: 1.5, borderRadius: '8px',
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid rgba(16, 185, 129, 0.2)',
                  }}>
                    <Typography sx={{ color: theme.success, fontSize: '0.8rem', fontWeight: 600, mb: 0.5 }}>
                      参考答案
                    </Typography>
                    <Typography sx={{ color: theme.textSecondary, fontSize: '0.85rem' }}>
                      {q.reference_answer}
                    </Typography>
                  </Box>
                )}
              </Box>
            ))
          )}
        </DialogContent>
        <DialogActions sx={{ borderTop: `1px solid ${theme.border}`, p: 2 }}>
          <Button
            onClick={() => setViewQuestionsDialog({ open: false, questions: [], setName: '' })}
            sx={{
              color: theme.textSecondary,
              '&:hover': { background: 'rgba(255, 255, 255, 0.05)' },
            }}
          >
            关闭
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DigitalInterviewerPage;
