import { useState, useEffect, useRef, useCallback } from 'react';
import { CONFIG } from '../config';

/**
 * 客服WebSocket Hook（带自动重连）
 * 支持指数退避重连策略
 */
export const useCustomerServiceWS = () => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const wsRef = useRef(null);
  const retryTimeoutRef = useRef(null);
  const manualCloseRef = useRef(false);
  const mountedRef = useRef(true);
  const retryCountRef = useRef(0);  // 使用 Ref 而不是 state

  const maxRetries = 5;
  const baseDelay = 1000;
  const maxDelay = 30000;

  // 计算重连延迟（指数退避）
  const getRetryDelay = useCallback((attempt) => {
    const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
    return delay + Math.random() * 1000;
  }, []);

  // 连接 WebSocket
  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    // 清理旧连接
    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      const ws = new WebSocket(CONFIG.CUSTOMER_SERVICE_WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;

        console.log('Customer service WebSocket connected');
        setIsConnected(true);
        setIsReconnecting(false);
        retryCountRef.current = 0;  // 连接成功后重置重试计数

        // 尝试恢复之前的会话
        const savedSessionId = localStorage.getItem('customer_service_session_id');
        if (savedSessionId) {
          console.log('Attempting to resume session:', savedSessionId);
          ws.send(JSON.stringify({
            type: 'resume_session',
            session_id: savedSessionId
          }));
        }
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;

        const data = JSON.parse(event.data);
        console.log('Received:', data);

        if (data.type === 'session_created') {
          setSessionId(data.session_id);
          localStorage.setItem('customer_service_session_id', data.session_id);
          console.log('New session created:', data.session_id);
        } else if (data.type === 'session_resumed') {
          setSessionId(data.session_id);
          console.log('Session resumed successfully:', data.session_id);
        } else if (data.type === 'response') {
          // 非流式：直接添加完整消息
          setMessages(prev => [...prev, {
            sender: 'bot',
            content: data.response,
            metadata: {
              confidence: data.confidence,
              match_type: data.match_type,
              transfer_to_human: data.transfer_to_human,
              matched_topic: data.matched_topic
            },
            timestamp: new Date()
          }]);
          setIsLoading(false);
        } else if (data.type === 'metadata') {
          // 流式模式元数据
          console.log('Metadata:', data);
        } else if (data.type === 'chunk') {
          // 流式模式内容块
          setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.sender === 'bot' && lastMsg.isStreaming) {
              return [
                ...prev.slice(0, -1),
                { ...lastMsg, content: lastMsg.content + data.content }
              ];
            } else {
              return [...prev, {
                sender: 'bot',
                content: data.content,
                isStreaming: true,
                timestamp: new Date()
              }];
            }
          });
        } else if (data.type === 'end') {
          // 流式结束
          setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.isStreaming) {
              return [
                ...prev.slice(0, -1),
                { ...lastMsg, isStreaming: false }
              ];
            }
            return prev;
          });
          setIsLoading(false);
        } else if (data.type === 'error') {
          console.error('Error:', data.content);
          setMessages(prev => [...prev, {
            sender: 'system',
            content: data.content,
            isError: true,
            timestamp: new Date()
          }]);
          setIsLoading(false);
        }
      };

      ws.onerror = (error) => {
        if (!mountedRef.current) return;
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;

        console.log('Customer service WebSocket disconnected');
        setIsConnected(false);

        // 如果不是手动关闭，尝试重连
        if (!manualCloseRef.current && retryCountRef.current < maxRetries) {
          setIsReconnecting(true);
          const delay = getRetryDelay(retryCountRef.current);

          console.log(`Reconnecting in ${Math.round(delay)}ms (attempt ${retryCountRef.current + 1}/${maxRetries})...`);

          retryTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              retryCountRef.current = retryCountRef.current + 1;
              connect();
            }
          }, delay);
        } else if (retryCountRef.current >= maxRetries) {
          setIsReconnecting(false);
          console.error('Max retries reached, giving up');
        }
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }, []);  // 移除 retryCount 依赖，避免无限循环

  // 初始化连接
  useEffect(() => {
    mountedRef.current = true;
    manualCloseRef.current = false;
    connect();

    return () => {
      mountedRef.current = false;
      manualCloseRef.current = true;

      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }

      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // 心跳保活机制
  useEffect(() => {
    if (!isConnected || !wsRef.current) return;

    const heartbeatInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
        console.log('Heartbeat sent');
      }
    }, 30000); // 30秒

    return () => clearInterval(heartbeatInterval);
  }, [isConnected]);

  // 手动重连
  const reconnect = useCallback(() => {
    manualCloseRef.current = false;
    retryCountRef.current = 0;
    setMessages([]); // 清空消息
    connect();
  }, [connect]);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // 添加用户消息到列表
      setMessages(prev => [...prev, {
        sender: 'user',
        content: message,
        timestamp: new Date()
      }]);

      // 设置加载状态
      setIsLoading(true);

      // 发送到服务器（非流式模式）
      wsRef.current.send(JSON.stringify({ message, stream: false }));
    } else {
      console.error('WebSocket is not connected');
      setMessages(prev => [...prev, {
        sender: 'system',
        content: '连接已断开，请刷新页面或点击重连',
        isError: true,
        timestamp: new Date()
      }]);
    }
  }, []);

  return {
    messages,
    isConnected,
    isReconnecting,
    retryCount: retryCountRef.current,  // 返回 ref 的当前值
    maxRetries,
    sessionId,
    isLoading,
    sendMessage,
    reconnect
  };
};
