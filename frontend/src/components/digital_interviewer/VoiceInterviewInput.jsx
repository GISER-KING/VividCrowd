import React, { useState, useRef, useEffect } from 'react';
import { Box, Button, Typography, CircularProgress, Alert } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import CheckIcon from '@mui/icons-material/Check';
import { MediaRecorder as ExtendableMediaRecorder, register } from 'extendable-media-recorder';
import { connect } from 'extendable-media-recorder-wav-encoder';
import { CONFIG } from '../../config';

/**
 * 语音面试输入组件
 * - 录制用户语音
 * - 点击"回答完毕"后调用ASR转文字
 * - 返回识别的文字给父组件
 */
const VoiceInterviewInput = ({ onAnswerComplete, disabled, isInterviewerSpeaking }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState('');

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);
  const timerRef = useRef(null);

  // 初始化WAV编码器
  useEffect(() => {
    const initWavEncoder = async () => {
      try {
        await register(await connect());
        console.log("WAV编码器已注册");
      } catch (e) {
        if (!e.message?.includes("already an encoder stored")) {
          console.error("WAV编码器注册失败", e);
        }
      }
    };
    initWavEncoder();

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // 开始录音
  const startRecording = async () => {
    try {
      setError('');
      chunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      });
      streamRef.current = stream;

      const recorder = new ExtendableMediaRecorder(stream, { mimeType: 'audio/wav' });

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start(1000); // 每秒收集一次数据
      setIsRecording(true);
      setRecordingTime(0);

      // 开始计时
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error("无法访问麦克风:", err);
      setError("无法访问麦克风，请检查权限设置");
    }
  };

  // 停止录音并处理
  const stopAndProcess = async () => {
    if (!mediaRecorderRef.current || mediaRecorderRef.current.state !== 'recording') {
      return;
    }

    // 停止计时
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    setIsRecording(false);
    setIsProcessing(true);

    // 停止录音
    mediaRecorderRef.current.stop();

    // 等待数据收集完成
    await new Promise(resolve => setTimeout(resolve, 500));

    // 停止媒体流
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // 检查录音时长
    if (recordingTime < 1) {
      setError("录音时间太短，请重新回答");
      setIsProcessing(false);
      return;
    }

    // 创建音频Blob
    const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
    chunksRef.current = [];

    // 调用ASR
    try {
      const formData = new FormData();
      formData.append('file', blob, 'answer.wav');

      const response = await fetch(`${CONFIG.API_BASE_URL}/digital-interviewer/audio/transcribe`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        if (data.text && data.text.trim()) {
          onAnswerComplete(data.text.trim());
        } else {
          setError("未能识别语音内容，请重新回答");
        }
      } else {
        setError("语音识别失败，请重试");
      }
    } catch (err) {
      console.error("ASR请求失败:", err);
      setError("语音识别服务异常，请重试");
    } finally {
      setIsProcessing(false);
      setRecordingTime(0);
    }
  };

  // 格式化时间
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 面试官正在说话时禁用
  const isDisabled = disabled || isInterviewerSpeaking || isProcessing;

  return (
    <Box sx={{ textAlign: 'center' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {isInterviewerSpeaking && (
        <Typography variant="body2" color="primary" sx={{ mb: 2 }}>
          面试官正在提问，请仔细聆听...
        </Typography>
      )}

      {!isRecording && !isProcessing && !isInterviewerSpeaking && (
        <Button
          variant="contained"
          color="primary"
          size="large"
          startIcon={<MicIcon />}
          onClick={startRecording}
          disabled={isDisabled}
          sx={{ minWidth: 200 }}
        >
          开始回答
        </Button>
      )}

      {isRecording && (
        <Box>
          <Box sx={{ mb: 2 }}>
            <Typography variant="h4" color="error">
              {formatTime(recordingTime)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              正在录音...
            </Typography>
          </Box>

          <Button
            variant="contained"
            color="success"
            size="large"
            startIcon={<CheckIcon />}
            onClick={stopAndProcess}
            sx={{ minWidth: 200 }}
          >
            回答完毕
          </Button>
        </Box>
      )}

      {/* ASR处理时不显示加载动画，静默处理 */}
    </Box>
  );
};

export default VoiceInterviewInput;
