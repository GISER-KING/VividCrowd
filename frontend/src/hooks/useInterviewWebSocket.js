import { useState, useEffect, useRef, useCallback } from 'react';

const useInterviewWebSocket = (sessionId) => {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;

    // WebSocket连接 - 使用相对路径通过Vite代理
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.host;
    const wsUrl = `${wsProtocol}//${wsHost}/api/digital-interviewer/training/ws/${sessionId}`;
    console.log('正在连接WebSocket:', wsUrl);

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket已连接');
      setConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('收到WebSocket消息:', data);
        setMessages(prev => [...prev, data]);
      } catch (err) {
        console.error('解析消息失败:', err);
      }
    };

    ws.onerror = (err) => {
      setError('WebSocket连接错误');
      console.error('WebSocket错误:', err);
    };

    ws.onclose = () => {
      console.log('WebSocket已断开');
      setConnected(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [sessionId]);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('发送WebSocket消息:', message);
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket未连接，无法发送消息');
    }
  }, []);

  return {
    connected,
    messages,
    error,
    sendMessage
  };
};

export default useInterviewWebSocket;
