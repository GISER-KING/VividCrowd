import React, { useRef, useEffect, useState } from 'react';
import { Box, Typography } from '@mui/material';

const VIDEO_STATES = ['idle', 'speaking', 'listening', 'thinking'];

const DigitalHumanPlayer = ({ videoUrls, currentState = 'idle' }) => {
  const videoRefs = useRef({});
  const [loadedStates, setLoadedStates] = useState({});
  const [error, setError] = useState('');

  // 预加载所有视频
  useEffect(() => {
    if (!videoUrls) return;

    VIDEO_STATES.forEach(state => {
      if (videoUrls[state] && videoRefs.current[state]) {
        const video = videoRefs.current[state];
        video.src = videoUrls[state];
        video.load();
      }
    });
  }, [videoUrls]);

  // 切换当前播放的视频
  useEffect(() => {
    if (!videoUrls) return;

    VIDEO_STATES.forEach(state => {
      const video = videoRefs.current[state];
      if (!video) return;

      if (state === currentState) {
        // 播放当前状态的视频
        video.currentTime = 0;
        video.play().catch(err => {
          console.error(`播放 ${state} 视频失败:`, err);
        });
      } else {
        // 暂停其他视频
        video.pause();
      }
    });
  }, [currentState, videoUrls]);

  const handleLoadedData = (state) => {
    setLoadedStates(prev => ({ ...prev, [state]: true }));
    setError('');
  };

  const handleError = (state) => {
    console.error(`视频 ${state} 加载失败`);
    // 只有当前状态加载失败才显示错误
    if (state === currentState) {
      setError('视频加载失败');
    }
  };

  const isLoading = videoUrls && !loadedStates[currentState];

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: '#000',
        borderRadius: 2,
        overflow: 'hidden',
        position: 'relative'
      }}
    >
      {isLoading && (
        <Box sx={{
          position: 'absolute',
          zIndex: 10,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          height: '100%',
          bgcolor: 'rgba(0,0,0,0.8)'
        }}>
          <Typography color="white">加载中...</Typography>
        </Box>
      )}

      {error && (
        <Box sx={{
          position: 'absolute',
          zIndex: 10,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          height: '100%',
          bgcolor: 'rgba(0,0,0,0.8)'
        }}>
          <Typography color="error">{error}</Typography>
        </Box>
      )}

      {/* 为每个状态创建一个 video 元素 */}
      {VIDEO_STATES.map(state => (
        <video
          key={state}
          ref={el => videoRefs.current[state] = el}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            position: 'absolute',
            top: 0,
            left: 0,
            opacity: state === currentState ? 1 : 0,
            transition: 'opacity 0.3s ease',
            pointerEvents: state === currentState ? 'auto' : 'none'
          }}
          loop={true}
          muted
          playsInline
          preload="auto"
          onLoadedData={() => handleLoadedData(state)}
          onError={() => handleError(state)}
        />
      ))}
    </Box>
  );
};

export default DigitalHumanPlayer;
