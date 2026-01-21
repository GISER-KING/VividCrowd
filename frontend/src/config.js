// 前端全局配置文件
// 所有请求通过 Vite 代理转发，使用相对路径

// 获取当前主机地址（用于WebSocket）
const getWsProtocol = () => window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const getWsHost = () => window.location.host;

export const CONFIG = {
    // WebSocket 地址（通过Vite代理转发）
    WS_URL: `${getWsProtocol()}//${getWsHost()}/api/chat/ws`,

    // 名人对话 WebSocket 地址
    CELEBRITY_WS_URL: `${getWsProtocol()}//${getWsHost()}/api/celebrity/ws`,

    // 客服对话 WebSocket 地址
    CUSTOMER_SERVICE_WS_URL: `${getWsProtocol()}//${getWsHost()}/api/customer-service/ws`,

    // API 基础地址（通过Vite代理转发）
    API_BASE_URL: '/api',

    // 群聊标题
    CHAT_TITLE: 'VividCrowd',

    // 头像配色 (可以根据需要添加更多)
    AVATAR_COLORS: {
        '小林': '#ff9800',  // 橙色
        '张遥': '#2196f3',  // 蓝色
        '甜糖': '#e91e63',  // 粉色
        '你': '#4caf50',    // 绿色
        'System': '#9e9e9e' // 灰色
    },

    // 默认头像颜色 (当名字未在上面定义时使用)
    DEFAULT_AVATAR_COLOR: '#607d8b'
};
