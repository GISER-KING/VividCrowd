import { useCallback, useRef, useState } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { CONFIG } from '../config';

/**
 * 名人对话 WebSocket Hook
 * @param {Array} selectedCelebrities - 选中的名人列表
 * @param {string} chatMode - 'private' | 'group'
 */
function useCelebrityWebSocket(selectedCelebrities, chatMode) {
  const [messages, setMessages] = useState([]);
  const [typingStatus, setTypingStatus] = useState('');
  const incomingBuffer = useRef({});

  const celebrityIds = selectedCelebrities.map(c => c.id);

  const { sendMessage: wsSend, lastMessage, readyState } = useWebSocket(
    selectedCelebrities.length > 0 ? CONFIG.CELEBRITY_WS_URL : null,
    {
      shouldReconnect: () => true,
      onMessage: (event) => {
        try {
          const data = JSON.parse(event.data);
          handleIncomingMessage(data);
        } catch (e) {
          console.error("Parse error", e);
        }
      }
    }
  );

  const handleIncomingMessage = useCallback((data) => {
    const { type, sender, content } = data;

    if (type === 'stream_start') {
      incomingBuffer.current[sender] = '';
      setTypingStatus(`${sender} 正在输入...`);

    } else if (type === 'stream_chunk') {
      if (incomingBuffer.current[sender] !== undefined) {
        incomingBuffer.current[sender] += content;
      }

    } else if (type === 'stream_end') {
      const fullContent = incomingBuffer.current[sender];
      delete incomingBuffer.current[sender];
      setTypingStatus('');

      if (fullContent && fullContent !== "...") {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + Math.random(),
            sender: sender,
            content: fullContent,
            isUser: false,
          }
        ]);
      }
    } else if (type === 'error') {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          sender: 'System',
          content: content,
          isUser: false,
          isError: true,
        }
      ]);
    }
  }, []);

  const sendMessage = useCallback((text) => {
    if (!text.trim() || celebrityIds.length === 0) return;

    // 添加用户消息到列表
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        sender: '你',
        content: text,
        isUser: true,
      }
    ]);

    // 发送到服务器
    wsSend(JSON.stringify({
      message: text,
      celebrity_ids: celebrityIds,
      mode: chatMode,
    }));
  }, [wsSend, celebrityIds, chatMode]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    sendMessage,
    clearMessages,
    typingStatus,
    isConnected: readyState === ReadyState.OPEN,
    readyState,
  };
}

export default useCelebrityWebSocket;
