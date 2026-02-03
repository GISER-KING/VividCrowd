# VividCrowd 更新日志

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### 新增
- 完善的 README 文档（中英文）
- 生产环境部署指南
- Docker 部署方案
- 安全注意事项章节
- 常见问题 FAQ
- 安装故障排查指南
- API 使用代码示例（Python/JavaScript/cURL）
- 性能指标与基准测试数据
- 环境变量完整列表
- 一键启动脚本（start.sh / start.bat）
- 停止服务脚本（stop.sh / stop.bat）
- 环境变量模板文件（.env.example）

---

## [1.1.0] - 2026-02-04

### 新增
- 🎉 PDF/Markdown 报告导出功能
- 🎉 Copilot 对话历史持久化
- 🎉 训练记录可点击查看历史报告
- 🎉 Copilot 对话自动保存（基于 sessionId）
- 📊 完整的评价报告导出（支持多页 PDF）

### 修复
- 🐛 修复训练完成对话框重叠问题（先关闭阶段评价）
- 🐛 修复评价报告分数显示错误（访问正确的嵌套结构）
- 🐛 修复 PDF 多页导出问题（正确的打印样式和分页）
- 🐛 移除 Copilot 聊天窗口的重复建议

### 改进
- ⚡ 升级所有 AI 模型至 qwen-max
- ⚡ 添加反幻觉指令提升回复质量
- ⚡ 训练记录添加悬停效果和指针光标
- 💾 新增 CopilotMessage 模型用于持久化对话
- 🧠 CustomerAgent 支持对话上下文感知（最近 5 轮）

### 技术改进
- 后端添加 WeasyPrint 和 Pillow 用于 PDF 生成
- 前端优化打印样式，支持多页导出
- 数据库新增 CopilotMessage 表
- API 新增 Copilot 消息持久化和检索端点

---

## [1.0.0] - 2026-01-20

### 新增
- ✨ 智能群聊功能
  - 深度拟人化 Agent
  - 混合路由架构（Fast & Slow Path）
  - 多重安全围栏
  - 深夜模式
  - 打字延迟模拟

- ✨ 数字分身功能
  - PDF 智能解析（人物/书籍/课程）
  - 多模态交互（语音/视频）
  - 双模式对话（私聊/群聊）
  - 知识检索增强（BM25 + Embedding）

- ✨ 数字客服功能
  - BM25 + Embedding 混合匹配
  - 置信度分层策略
  - 智能转人工
  - CSV 数据导入
  - 会话管理与统计

- ✨ 销售演练功能
  - 五阶段销售流程控制
  - 实时评价引擎
  - AI 销售助手（Sales Copilot）
  - 沉浸式客户模拟
  - 综合评价报告（雷达图）

### 技术栈
- 后端：FastAPI + SQLAlchemy + DashScope
- 前端：React + Vite + Material-UI
- 数据库：SQLite（三数据库分离架构）
- AI 模型：Qwen-Max/Plus/Turbo + text-embedding-v2

---

## 版本说明

### 版本号格式：主版本号.次版本号.修订号

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 变更类型

- **新增 (Added)**：新功能
- **修复 (Fixed)**：Bug 修复
- **改进 (Changed)**：现有功能的变更
- **弃用 (Deprecated)**：即将移除的功能
- **移除 (Removed)**：已移除的功能
- **安全 (Security)**：安全相关的修复

---

[Unreleased]: https://github.com/your-username/VividCrowd/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/your-username/VividCrowd/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/your-username/VividCrowd/releases/tag/v1.0.0
