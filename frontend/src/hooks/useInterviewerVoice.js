import { useRef, useCallback } from 'react';
import { CONFIG } from '../config';

/**
 * TTS语音播放Hook
 * 用于播放面试官的语音提问
 * 支持预加载功能，实现文字和语音同步
 */
const useInterviewerVoice = () => {
  const audioRef = useRef(null);
  const isPlayingRef = useRef(false);

  // 预加载TTS语音，返回播放函数
  const preload = useCallback(async (text, voice = 'longyuan') => {
    if (!text) return null;

    try {
      // 调用TTS API
      const formData = new FormData();
      formData.append('text', text);
      formData.append('voice', voice);

      const response = await fetch(`${CONFIG.API_BASE_URL}/digital-interviewer/audio/synthesize`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('TTS请求失败');
      }

      // 获取音频数据
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      // 创建Audio元素并预加载
      const audio = new Audio();
      audio.src = audioUrl;
      audio.preload = 'auto';

      // 等待音频加载完成
      await new Promise((resolve, reject) => {
        audio.oncanplaythrough = resolve;
        audio.onerror = reject;
        // 超时处理
        setTimeout(() => resolve(), 5000);
      });

      // 返回播放函数
      return () => {
        return new Promise((resolve, reject) => {
          if (isPlayingRef.current) {
            // 如果正在播放，先停止
            if (audioRef.current) {
              audioRef.current.pause();
            }
          }

          isPlayingRef.current = true;
          audioRef.current = audio;

          audio.onended = () => {
            isPlayingRef.current = false;
            URL.revokeObjectURL(audioUrl);
            resolve();
          };

          audio.onerror = (err) => {
            isPlayingRef.current = false;
            URL.revokeObjectURL(audioUrl);
            reject(err);
          };

          audio.play().catch(err => {
            isPlayingRef.current = false;
            URL.revokeObjectURL(audioUrl);
            reject(err);
          });
        });
      };

    } catch (err) {
      console.error('TTS预加载失败:', err);
      return null;
    }
  }, []);

  // 直接播放TTS语音（不预加载）
  const speak = useCallback(async (text, voice = 'longyuan') => {
    const playFn = await preload(text, voice);
    if (playFn) {
      return playFn();
    }
  }, [preload]);

  // 停止播放
  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    isPlayingRef.current = false;
  }, []);

  // 检查是否正在播放
  const isPlaying = useCallback(() => {
    return isPlayingRef.current;
  }, []);

  return {
    speak,
    preload,
    stop,
    isPlaying
  };
};

export default useInterviewerVoice;
