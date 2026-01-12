// 前端全局配置文件

export const CONFIG = {
    // 后端 WebSocket 地址
    WS_URL: 'ws://localhost:8000/ws',
    
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
