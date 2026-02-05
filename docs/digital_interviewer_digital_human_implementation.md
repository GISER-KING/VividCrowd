# 数字面试官虚拟人形象库实现文档

## 📋 架构重构说明

### 原架构（错误）
- 每个面试官有多个虚拟形象（如张伟有default、formal、casual三个形象）
- 虚拟形象属于特定面试官
- 目录结构：`interviewer_videos/{interviewer_id}/{avatar_name}/`

### 新架构（正确）
- **虚拟人形象库**：独立的虚拟人形象，不属于任何面试官
- **面试官画像**：专业信息、面试风格（不包含视频）
- **灵活组合**：任意面试官 + 任意虚拟人形象
- 目录结构：`digital_humans/{human_name}/`

## 🎯 核心概念

### 1. 面试官画像（InterviewerProfile）
- 定义：面试官的专业信息、面试风格、问题偏好
- 不包含：视频文件
- 示例：张伟（技术专家）、李娜（HR经理）

### 2. 虚拟人形象（DigitalHuman）
- 定义：纯粹的视觉展示，包含4个状态视频
- 独立存在：不属于任何特定面试官
- 示例：男性正式形象、女性休闲形象、技术极客形象

### 3. 使用方式
用户选择：**面试官** + **虚拟人形象** → 开始面试

### 4. 优势
- ✅ 形象复用：一个虚拟人形象可用于多个面试官
- ✅ 解耦设计：面试官画像和视觉展示完全分离
- ✅ 灵活组合：任意面试官可使用任意虚拟人形象

## 🏗️ 数据库设计

### 新增表：DigitalHuman

```python
class DigitalHuman(Base):
    """虚拟人形象表 - 存储独立的虚拟人形象库"""
    __tablename__ = "digital_humans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    gender = Column(String(20), nullable=True)  # male/female/other
    style = Column(String(50), nullable=True)   # formal/casual/tech

    # 视频路径
    video_idle = Column(String(500), nullable=True)
    video_speaking = Column(String(500), nullable=True)
    video_listening = Column(String(500), nullable=True)
    video_thinking = Column(String(500), nullable=True)

    # 状态
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
```

### 修改表：InterviewerProfile

**移除字段**：
- ~~video_idle~~
- ~~video_speaking~~
- ~~video_listening~~
- ~~video_thinking~~

面试官画像不再包含视频字段。

### 修改表：InterviewSession

**修改字段**：
- ~~interviewer_avatar_id~~ → `digital_human_id`

会话记录使用的虚拟人形象ID。

### 删除表：InterviewerAvatar

旧的面试官虚拟形象表已被DigitalHuman替代。

## 📁 文件系统设计

### 目录结构

```
backend/data/digital_humans/
├── male_formal/          # 男性正式形象
│   ├── idle.mp4
│   ├── speaking.mp4
│   ├── listening.mp4
│   └── thinking.mp4
├── female_casual/        # 女性休闲形象
│   ├── idle.mp4
│   ├── speaking.mp4
│   ├── listening.mp4
│   └── thinking.mp4
├── tech_geek/            # 技术极客形象
│   ├── idle.mp4
│   ├── speaking.mp4
│   ├── listening.mp4
│   └── thinking.mp4
└── README.md
```

### 命名规范

- 使用小写字母和下划线
- 建议格式：`{性别}_{风格}`
- 示例：`male_formal`, `female_casual`, `tech_geek`

## 🔧 后端实现

### 1. 扫描函数

```python
def scan_all_digital_humans():
    """启动时扫描所有虚拟人形象"""
    # 遍历 digital_humans 目录
    # 检查每个子目录的4个视频文件
    # 创建或更新 DigitalHuman 记录
    # 自动提取性别和风格信息
```

### 2. API端点

#### 获取虚拟人形象列表
```
GET /api/digital-interviewer/digital-humans
```

返回所有可用的虚拟人形象。

#### 创建面试会话
```
POST /api/digital-interviewer/sessions/start
```

参数：
- `interviewer_id`: 面试官ID
- `interview_type`: 面试类型
- `candidate_name`: 候选人姓名
- `digital_human_id`: 虚拟人形象ID（新增）

返回：
- `session_id`: 会话ID
- `digital_human_videos`: 虚拟人形象的视频URL

### 3. 启动时扫描

```python
# main.py
from backend.apps.digital_interviewer.app import scan_all_digital_humans

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    scan_all_digital_humans()
    yield
```

## 🎨 前端实现

### 1. 状态管理

```javascript
// 虚拟人形象状态
const [digitalHumans, setDigitalHumans] = useState([]);
const [selectedDigitalHuman, setSelectedDigitalHuman] = useState(null);
const [digitalHumanVideos, setDigitalHumanVideos] = useState(null);
```

### 2. 获取虚拟人形象列表

```javascript
const fetchDigitalHumans = async () => {
  const response = await axios.get('/api/digital-interviewer/digital-humans');
  const humanList = response.data.digital_humans || [];
  setDigitalHumans(humanList);

  // 自动选择默认形象
  const defaultHuman = humanList.find(h => h.is_default);
  if (defaultHuman) {
    setSelectedDigitalHuman(defaultHuman);
  }
};
```

### 3. UI组件

```jsx
<TextField
  fullWidth
  select
  label="虚拟人形象"
  value={selectedDigitalHuman?.id || ''}
  onChange={(e) => {
    const human = digitalHumans.find(h => h.id === parseInt(e.target.value));
    setSelectedDigitalHuman(human);
  }}
>
  {digitalHumans.map((human) => (
    <MenuItem key={human.id} value={human.id}>
      {human.display_name} {human.is_default ? '(默认)' : ''}
    </MenuItem>
  ))}
</TextField>
```

### 4. 开始面试

```javascript
const handleStartInterview = async () => {
  const formData = new FormData();
  formData.append('interviewer_id', selectedInterviewer.id);
  formData.append('interview_type', interviewType);
  formData.append('candidate_name', candidateName);
  formData.append('digital_human_id', selectedDigitalHuman.id);

  const response = await axios.post('/api/digital-interviewer/sessions/start', formData);

  // 保存虚拟人形象视频URL
  if (response.data.digital_human_videos) {
    setDigitalHumanVideos(response.data.digital_human_videos);
  }
};
```

## 🔄 工作流程

### 1. 准备阶段

1. 创建虚拟人形象目录：`backend/data/digital_humans/male_formal/`
2. 放置4个视频文件：`idle.mp4`, `speaking.mp4`, `listening.mp4`, `thinking.mp4`

### 2. 扫描阶段

1. 后端启动时调用 `scan_all_digital_humans()`
2. 遍历 `digital_humans` 目录
3. 检查每个子目录的视频文件
4. 创建/更新 `DigitalHuman` 记录

### 3. 选择阶段

1. 前端调用 `/api/digital-interviewer/digital-humans` 获取虚拟人形象列表
2. 显示虚拟人形象下拉框
3. 用户选择面试官 + 虚拟人形象

### 4. 面试阶段

1. 用户点击"开始面试"
2. 前端发送 `digital_human_id` 到后端
3. 后端创建会话，记录 `digital_human_id`
4. 后端返回虚拟人形象的视频URL
5. 前端使用这些URL播放数字人视频

## 📊 数据流

```
文件系统 (digital_humans/)
  ↓ (后端启动时扫描)
数据库 (digital_humans表)
  ↓ (API查询)
前端 (虚拟人形象列表)
  ↓ (用户选择)
会话创建 (记录digital_human_id)
  ↓ (返回视频URL)
视频播放 (DigitalHumanPlayer)
```

## 🧪 测试步骤

### 1. 准备测试数据

```bash
# 创建测试虚拟人形象
mkdir -p backend/data/digital_humans/male_formal
mkdir -p backend/data/digital_humans/female_casual

# 放置测试视频（可以使用同一个视频）
cp test_video.mp4 backend/data/digital_humans/male_formal/idle.mp4
cp test_video.mp4 backend/data/digital_humans/male_formal/speaking.mp4
cp test_video.mp4 backend/data/digital_humans/male_formal/listening.mp4
cp test_video.mp4 backend/data/digital_humans/male_formal/thinking.mp4

cp test_video.mp4 backend/data/digital_humans/female_casual/idle.mp4
cp test_video.mp4 backend/data/digital_humans/female_casual/speaking.mp4
cp test_video.mp4 backend/data/digital_humans/female_casual/listening.mp4
cp test_video.mp4 backend/data/digital_humans/female_casual/thinking.mp4
```

### 2. 启动后端

```bash
cd backend
python main.py
```

检查日志输出：
```
🎭 开始扫描虚拟人形象库...
🎭 扫描虚拟人形象: male_formal
  ✅ idle.mp4
  ✅ speaking.mp4
  ✅ listening.mp4
  ✅ thinking.mp4
  ✨ 新增虚拟人形象: Male Formal
🎭 扫描虚拟人形象: female_casual
  ✅ idle.mp4
  ✅ speaking.mp4
  ✅ listening.mp4
  ✅ thinking.mp4
  ✨ 新增虚拟人形象: Female Casual
✅ 扫描完成，共找到 2 个虚拟人形象
```

### 3. 测试前端

1. 访问数字面试官页面
2. 选择一个面试官
3. 检查"虚拟人形象"下拉框是否显示 "Male Formal" 和 "Female Casual"
4. 选择不同的虚拟人形象
5. 点击"开始面试"
6. 检查数字人视频是否正确播放

### 4. 验证数据库

```bash
cd backend
python -c "
from core.database import digital_interviewer_sync_session
from models.db_models import DigitalHuman, InterviewSession

db = digital_interviewer_sync_session()

# 查看虚拟人形象
humans = db.query(DigitalHuman).all()
for human in humans:
    print(f'形象: {human.display_name}, 性别: {human.gender}, 风格: {human.style}')

# 查看会话记录
sessions = db.query(InterviewSession).all()
for session in sessions:
    print(f'会话: {session.session_id}, 使用虚拟人ID: {session.digital_human_id}')
"
```

## 📚 相关文档

- **用户文档**：`backend/data/digital_humans/README.md`
- **示例目录**：`backend/data/digital_humans/EXAMPLE/`
- **数据库模型**：`backend/models/db_models.py`
- **后端路由**：`backend/apps/digital_interviewer/app.py`
- **前端页面**：`frontend/src/pages/DigitalInterviewerPage.jsx`

## ✅ 完成清单

- [x] 创建 DigitalHuman 数据库模型
- [x] 从 InterviewerProfile 移除视频字段
- [x] 在 InterviewSession 中将 interviewer_avatar_id 改为 digital_human_id
- [x] 删除 InterviewerAvatar 模型
- [x] 创建 digital_humans 目录结构
- [x] 实现 scan_all_digital_humans() 函数
- [x] 在后端启动时调用扫描函数
- [x] 添加获取虚拟人形象列表的API端点
- [x] 修改会话创建端点支持 digital_human_id
- [x] 删除旧的上传视频端点
- [x] 前端添加虚拟人形象状态管理
- [x] 前端添加虚拟人形象选择器UI
- [x] 前端传递 digital_human_id 到后端
- [x] 前端接收并使用虚拟人形象视频URL
- [x] 更新 README 文档
- [x] 创建示例目录结构

## 🎉 功能特点

1. **独立形象库**：虚拟人形象独立于面试官，可复用
2. **灵活组合**：任意面试官可使用任意虚拟人形象
3. **自动扫描**：后端启动时自动扫描，无需手动导入
4. **智能识别**：自动从目录名提取性别和风格信息
5. **用户友好**：前端提供直观的下拉选择器
6. **可追溯**：会话记录中保存使用的虚拟人形象ID

## 🔮 使用场景

### 场景1：多个面试官使用同一个形象
```
面试官A（技术专家） + 男性正式形象 = 技术面试
面试官B（HR经理） + 男性正式形象 = HR面试
```

### 场景2：同一个面试官使用不同形象
```
面试官A（技术专家） + 男性正式形象 = 正式技术面试
面试官A（技术专家） + 男性休闲形象 = 轻松技术面试
```

### 场景3：灵活组合
```
面试官A（技术专家） + 女性技术形象 = 女性技术面试官
面试官B（HR经理） + 男性休闲形象 = 轻松HR面试
```

## 📅 实现日期

2026-02-05

## 👤 实现者

Claude Sonnet 4.5
