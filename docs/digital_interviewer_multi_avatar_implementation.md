# 数字面试官多虚拟形象功能实现文档

## 📋 功能概述

为数字面试官子应用实现了多虚拟形象支持功能，允许每个面试官拥有多个不同风格的虚拟形象（如默认、正式、休闲等），用户在开始面试前可以选择使用哪个形象。

## 🎯 实现目标

1. ✅ 支持每个面试官拥有多个虚拟形象
2. ✅ 后端启动时自动扫描文件系统中的虚拟形象
3. ✅ 在数据库中维护虚拟形象表
4. ✅ 前端提供虚拟形象选择器
5. ✅ 面试会话记录使用的虚拟形象

## 🏗️ 架构设计

### 数据库层

#### 新增表：InterviewerAvatar

```python
class InterviewerAvatar(Base):
    """面试官虚拟形象表"""
    __tablename__ = "interviewer_avatars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    interviewer_profile_id = Column(Integer, ForeignKey("interviewer_profiles.id"))

    # 形象信息
    avatar_name = Column(String(50), nullable=False)  # 形象名称（如 default, formal, casual）
    display_name = Column(String(100), nullable=True)  # 显示名称

    # 视频路径
    video_idle = Column(String(500), nullable=True)
    video_speaking = Column(String(500), nullable=True)
    video_listening = Column(String(500), nullable=True)
    video_thinking = Column(String(500), nullable=True)

    # 状态
    is_default = Column(Boolean, default=False)  # 是否为默认形象
    is_active = Column(Boolean, default=True)    # 是否激活
```

#### 修改表：InterviewSession

新增字段：
```python
interviewer_avatar_id = Column(Integer, ForeignKey("interviewer_avatars.id"), nullable=True)
```

### 文件系统层

#### 目录结构

```
backend/data/interviewer_videos/
├── {interviewer_id}/          # 面试官ID（数字）
│   ├── default/               # 默认形象（必须）
│   │   ├── idle.mp4
│   │   ├── speaking.mp4
│   │   ├── listening.mp4
│   │   └── thinking.mp4
│   ├── formal/                # 正式形象（可选）
│   │   ├── idle.mp4
│   │   ├── speaking.mp4
│   │   ├── listening.mp4
│   │   └── thinking.mp4
│   └── ...                    # 其他自定义形象
```

### 后端API层

#### 新增端点

1. **获取虚拟形象列表**
   ```
   GET /api/digital-interviewer/interviewers/{interviewer_id}/avatars
   ```
   返回指定面试官的所有可用虚拟形象。

2. **修改会话创建端点**
   ```
   POST /api/digital-interviewer/sessions/start
   ```
   新增参数：`avatar_id`（可选）
   返回数据中包含：`avatar_videos`（虚拟形象的视频路径）

#### 核心函数

1. **scan_interviewer_avatars(interviewer_id, db)**
   - 扫描指定面试官的所有虚拟形象
   - 检查每个形象目录下的4个视频文件
   - 创建或更新数据库中的虚拟形象记录
   - 返回扫描到的形象数量

2. **scan_all_interviewer_avatars()**
   - 在后端启动时调用
   - 扫描所有面试官的虚拟形象
   - 更新数据库

### 前端层

#### 状态管理

新增状态：
```javascript
const [avatars, setAvatars] = useState([]);              // 虚拟形象列表
const [selectedAvatar, setSelectedAvatar] = useState(null);  // 选中的形象
const [loadingAvatars, setLoadingAvatars] = useState(false); // 加载状态
const [avatarVideos, setAvatarVideos] = useState(null);      // 当前使用的视频URL
```

#### UI组件

在"开始面试"表单中新增虚拟形象选择器：
```jsx
<TextField
  fullWidth
  select
  label="虚拟形象"
  value={selectedAvatar?.id || ''}
  onChange={(e) => {
    const avatar = avatars.find(a => a.id === parseInt(e.target.value));
    setSelectedAvatar(avatar);
  }}
  disabled={loadingAvatars || avatars.length === 0}
>
  {avatars.map((avatar) => (
    <MenuItem key={avatar.id} value={avatar.id}>
      {avatar.display_name} {avatar.is_default ? '(默认)' : ''}
    </MenuItem>
  ))}
</TextField>
```

## 📝 实现细节

### 1. 数据库模型更新

**文件**：`backend/models/db_models.py`

- 新增 `InterviewerAvatar` 模型
- 在 `InterviewSession` 中添加 `interviewer_avatar_id` 字段

### 2. 后端路由更新

**文件**：`backend/apps/digital_interviewer/app.py`

#### 修改点1：上传画像时扫描虚拟形象

```python
# 自动扫描虚拟形象
logger.info(f"🎬 扫描面试官虚拟形象...")
avatar_count = scan_interviewer_avatars(interviewer.id, db)
if avatar_count > 0:
    logger.info(f"✅ 找到 {avatar_count} 个虚拟形象")
```

#### 修改点2：新增获取虚拟形象列表端点

```python
@router.get("/interviewers/{interviewer_id}/avatars")
async def get_interviewer_avatars(interviewer_id: int, db: Session):
    avatars = db.query(InterviewerAvatar).filter_by(
        interviewer_profile_id=interviewer_id,
        is_active=True
    ).all()
    return {"avatars": [avatar.to_dict() for avatar in avatars]}
```

#### 修改点3：会话创建支持avatar_id

```python
@router.post("/sessions/start")
async def start_interview_session(
    interviewer_id: int = Form(...),
    interview_type: str = Form(...),
    candidate_name: str = Form(None),
    avatar_id: int = Form(None),  # 新增参数
    db: Session = Depends(get_digital_interviewer_db)
):
    # 验证虚拟形象
    avatar = None
    if avatar_id:
        avatar = db.query(InterviewerAvatar).filter_by(
            id=avatar_id,
            interviewer_profile_id=interviewer_id
        ).first()

    # 创建会话时记录avatar_id
    session = InterviewSession(
        session_id=session_id,
        interviewer_profile_id=interviewer_id,
        interviewer_avatar_id=avatar_id,  # 记录使用的形象
        # ...
    )

    # 返回虚拟形象视频路径
    if avatar:
        response_data["avatar_videos"] = {
            "idle": avatar.video_idle,
            "speaking": avatar.video_speaking,
            "listening": avatar.video_listening,
            "thinking": avatar.video_thinking
        }
```

### 3. 后端启动时扫描

**文件**：`backend/main.py`

```python
from backend.apps.digital_interviewer.app import scan_all_interviewer_avatars

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    # ...

    # 扫描数字面试官虚拟形象
    logger.info("扫描数字面试官虚拟形象...")
    scan_all_interviewer_avatars()
    logger.info("数字面试官初始化完成")

    yield
```

### 4. 前端页面更新

**文件**：`frontend/src/pages/DigitalInterviewerPage.jsx`

#### 修改点1：新增状态和获取虚拟形象函数

```javascript
// 获取虚拟形象列表
const fetchAvatars = async (interviewerId) => {
  setLoadingAvatars(true);
  try {
    const response = await axios.get(
      `/api/digital-interviewer/interviewers/${interviewerId}/avatars`
    );
    const avatarList = response.data.avatars || [];
    setAvatars(avatarList);

    // 自动选择默认形象
    const defaultAvatar = avatarList.find(a => a.is_default);
    if (defaultAvatar) {
      setSelectedAvatar(defaultAvatar);
    } else if (avatarList.length > 0) {
      setSelectedAvatar(avatarList[0]);
    }
  } catch (error) {
    console.error('获取虚拟形象列表失败:', error);
  } finally {
    setLoadingAvatars(false);
  }
};

// 当选择面试官时，获取其虚拟形象
useEffect(() => {
  if (selectedInterviewer) {
    fetchAvatars(selectedInterviewer.id);
  }
}, [selectedInterviewer]);
```

#### 修改点2：开始面试时传递avatar_id

```javascript
const handleStartInterview = async () => {
  if (!selectedAvatar) {
    alert('请先选择虚拟形象');
    return;
  }

  const formData = new FormData();
  formData.append('interviewer_id', selectedInterviewer.id);
  formData.append('interview_type', interviewType);
  formData.append('candidate_name', candidateName);
  formData.append('avatar_id', selectedAvatar.id);  // 传递形象ID

  const response = await axios.post('/api/digital-interviewer/sessions/start', formData);

  // 保存虚拟形象视频URL
  if (response.data.avatar_videos) {
    setAvatarVideos(response.data.avatar_videos);
  }
};
```

#### 修改点3：传递视频URL给DigitalHumanPlayer

```jsx
<DigitalHumanPlayer
  videoUrls={avatarVideos}
  currentState={currentVideoState}
/>
```

## 🔄 工作流程

### 1. 准备阶段

1. 用户上传面试官画像（PDF/Markdown）
2. 系统创建面试官记录，分配ID（如1）
3. 用户在文件系统中创建虚拟形象目录：
   ```
   backend/data/interviewer_videos/1/default/
   backend/data/interviewer_videos/1/formal/
   ```
4. 用户将视频文件放到对应目录

### 2. 扫描阶段

1. 后端启动时调用 `scan_all_interviewer_avatars()`
2. 遍历所有面试官
3. 对每个面试官调用 `scan_interviewer_avatars()`
4. 扫描子目录，检查视频文件
5. 创建/更新数据库中的 `InterviewerAvatar` 记录

### 3. 选择阶段

1. 用户在前端选择面试官
2. 前端调用 `/api/digital-interviewer/interviewers/{id}/avatars` 获取虚拟形象列表
3. 显示虚拟形象下拉框
4. 用户选择虚拟形象（默认自动选择default）

### 4. 面试阶段

1. 用户点击"开始面试"
2. 前端发送 `avatar_id` 到后端
3. 后端创建会话，记录 `interviewer_avatar_id`
4. 后端返回虚拟形象的视频URL
5. 前端使用这些URL播放数字人视频

## 📊 数据流

```
文件系统
  ↓ (后端启动时扫描)
数据库 (interviewer_avatars表)
  ↓ (API查询)
前端 (虚拟形象列表)
  ↓ (用户选择)
会话创建 (记录avatar_id)
  ↓ (返回视频URL)
视频播放 (DigitalHumanPlayer)
```

## 🧪 测试步骤

### 1. 准备测试数据

```bash
# 创建测试目录
mkdir -p backend/data/interviewer_videos/1/default
mkdir -p backend/data/interviewer_videos/1/formal

# 放置测试视频（可以使用同一个视频）
cp test_video.mp4 backend/data/interviewer_videos/1/default/idle.mp4
cp test_video.mp4 backend/data/interviewer_videos/1/default/speaking.mp4
cp test_video.mp4 backend/data/interviewer_videos/1/default/listening.mp4
cp test_video.mp4 backend/data/interviewer_videos/1/default/thinking.mp4

cp test_video.mp4 backend/data/interviewer_videos/1/formal/idle.mp4
cp test_video.mp4 backend/data/interviewer_videos/1/formal/speaking.mp4
cp test_video.mp4 backend/data/interviewer_videos/1/formal/listening.mp4
cp test_video.mp4 backend/data/interviewer_videos/1/formal/thinking.mp4
```

### 2. 启动后端

```bash
cd backend
python main.py
```

检查日志输出：
```
🎭 开始扫描所有面试官的虚拟形象...
📋 扫描面试官: 张伟 (ID: 1)
🎭 扫描形象: default
  ✅ idle.mp4
  ✅ speaking.mp4
  ✅ listening.mp4
  ✅ thinking.mp4
  ✨ 新增形象: default
🎭 扫描形象: formal
  ✅ idle.mp4
  ✅ speaking.mp4
  ✅ listening.mp4
  ✅ thinking.mp4
  ✨ 新增形象: formal
✅ 扫描完成，共找到 2 个虚拟形象
```

### 3. 测试前端

1. 访问数字面试官页面
2. 选择一个面试官
3. 检查"虚拟形象"下拉框是否显示 "Default (默认)" 和 "Formal"
4. 选择不同的形象
5. 点击"开始面试"
6. 检查数字人视频是否正确播放

### 4. 验证数据库

```bash
cd backend
python -c "
from core.database import digital_interviewer_sync_session
from models.db_models import InterviewerAvatar, InterviewSession

db = digital_interviewer_sync_session()

# 查看虚拟形象
avatars = db.query(InterviewerAvatar).all()
for avatar in avatars:
    print(f'形象: {avatar.display_name}, 面试官ID: {avatar.interviewer_profile_id}, 默认: {avatar.is_default}')

# 查看会话记录
sessions = db.query(InterviewSession).all()
for session in sessions:
    print(f'会话: {session.session_id}, 使用形象ID: {session.interviewer_avatar_id}')
"
```

## 📚 相关文档

- **用户文档**：`backend/data/interviewer_videos/README.md`
- **示例目录**：`backend/data/interviewer_videos/EXAMPLE/`
- **数据库模型**：`backend/models/db_models.py`
- **后端路由**：`backend/apps/digital_interviewer/app.py`
- **前端页面**：`frontend/src/pages/DigitalInterviewerPage.jsx`

## ✅ 完成清单

- [x] 创建 InterviewerAvatar 数据库模型
- [x] 在 InterviewSession 中添加 interviewer_avatar_id 字段
- [x] 实现 scan_interviewer_avatars() 函数
- [x] 实现 scan_all_interviewer_avatars() 函数
- [x] 在后端启动时调用扫描函数
- [x] 添加获取虚拟形象列表的API端点
- [x] 修改会话创建端点支持 avatar_id
- [x] 前端添加虚拟形象状态管理
- [x] 前端添加虚拟形象选择器UI
- [x] 前端传递 avatar_id 到后端
- [x] 前端接收并使用虚拟形象视频URL
- [x] 更新 README 文档
- [x] 创建示例目录结构

## 🎉 功能特点

1. **灵活性**：支持任意数量和名称的虚拟形象
2. **自动化**：后端启动时自动扫描，无需手动导入
3. **用户友好**：前端提供直观的下拉选择器
4. **可追溯**：会话记录中保存使用的虚拟形象ID
5. **扩展性**：易于添加新的虚拟形象，只需创建目录和放置视频

## 🔮 未来改进

1. 支持虚拟形象的在线预览
2. 支持虚拟形象的元数据（描述、标签等）
3. 支持虚拟形象的热更新（无需重启后端）
4. 支持虚拟形象的权限控制（某些形象仅特定用户可用）
5. 支持虚拟形象的使用统计和推荐

## 📅 实现日期

2026-02-05

## 👤 实现者

Claude Sonnet 4.5
