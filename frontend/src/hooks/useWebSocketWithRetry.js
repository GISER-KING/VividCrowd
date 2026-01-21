import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * 带自动重连的 WebSocket Hook
 * 支持指数退避重连策略
 *
 * @param {string} url - WebSocket URL
 * @param {Object} options - 配置选项
 * @param {number} options.maxRetries - 最大重试次数，默认 5
 * @param {number} options.baseDelay - 基础延迟时间（毫秒），默认 1000
 * @param {number} options.maxDelay - 最大延迟时间（毫秒），默认 30000
 * @param {Function} options.onMessage - 消息处理回调
 * @param {Function} options.onOpen - 连接打开回调
 * @param {Function} options.onClose - 连接关闭回调
 * @param {Function} options.onError - 错误回调
 * @param {Function} options.onReconnecting - 重连中回调
 * @param {Function} options.onMaxRetriesReached - 达到最大重试次数回调
 */
function useWebSocketWithRetry(url, options = {}) {
  const {
    maxRetries = 3,
    baseDelay = 5000,
    maxDelay = 30000,
    onMessage,
    onOpen,
    onClose,
    onError,
    onReconnecting,
    onMaxRetriesReached
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [connectionError, setConnectionError] = useState(null);

  const wsRef = useRef(null);
  const retryTimeoutRef = useRef(null);
  const manualCloseRef = useRef(false);
  const mountedRef = useRef(true);

  // 计算重连延迟（指数退避）
  const getRetryDelay = useCallback((attempt) => {
    const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
    // 添加一点随机性，避免所有客户端同时重连
    return delay + Math.random() * 1000;
  }, [baseDelay, maxDelay]);

  // 连接 WebSocket
  const connect = useCallback(() => {
    if (!mountedRef.current || !url) return;

    // 清理旧连接
    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        if (!mountedRef.current) return;

        setIsConnected(true);
        setIsReconnecting(false);
        setRetryCount(0);
        setConnectionError(null);

        onOpen?.();
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        onMessage?.(event);
      };

      ws.onerror = (error) => {
        if (!mountedRef.current) return;

        console.error('WebSocket error:', error);
        setConnectionError(error);
        onError?.(error);
      };

      ws.onclose = (event) => {
        if (!mountedRef.current) return;

        setIsConnected(false);
        onClose?.(event);

        // 如果不是手动关闭，尝试重连
        if (!manualCloseRef.current && retryCount < maxRetries) {
          setIsReconnecting(true);
          const delay = getRetryDelay(retryCount);

          onReconnecting?.(retryCount + 1, delay);

          retryTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              setRetryCount(prev => prev + 1);
              connect();
            }
          }, delay);
        } else if (retryCount >= maxRetries) {
          setIsReconnecting(false);
          onMaxRetriesReached?.();
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('WebSocket connection error:', error);
      setConnectionError(error);
    }
  }, [url, retryCount, maxRetries, getRetryDelay, onMessage, onOpen, onClose, onError, onReconnecting, onMaxRetriesReached]);

  // 发送消息
  const sendMessage = useCallback((data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      wsRef.current.send(message);
      return true;
    }
    return false;
  }, []);

  // 手动重连
  const reconnect = useCallback(() => {
    manualCloseRef.current = false;
    setRetryCount(0);
    connect();
  }, [connect]);

  // 手动关闭
  const disconnect = useCallback(() => {
    manualCloseRef.current = true;

    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
    }

    setIsConnected(false);
    setIsReconnecting(false);
    setRetryCount(0);
  }, []);

  // 初始化连接
  useEffect(() => {
    mountedRef.current = true;
    manualCloseRef.current = false;

    if (url) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      manualCloseRef.current = true;

      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }

      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]); // 只在 URL 变化时重新连接

  return {
    isConnected,
    isReconnecting,
    retryCount,
    maxRetries,
    connectionError,
    sendMessage,
    reconnect,
    disconnect,
    ws: wsRef.current
  };
}

export default useWebSocketWithRetry;
