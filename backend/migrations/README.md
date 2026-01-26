# 数据库分离迁移说明

## 概述

数据库已从单一的 `app.db` 分离为两个独立的数据库：

- **celebrity.db** - 存储数字名人相关数据
- **customerService.db** - 存储数字客服相关数据

## 数据库架构

### celebrity.db (数字名人数据库)
- **KnowledgeSource** - 名人/书籍/课程的基本信息
- **CelebrityChunk** - 文档分块和向量嵌入

### customerService.db (数字客服数据库)
- **CustomerServiceQA** - 客服问答知识库
- **CustomerServiceSession** - 客服会话记录
- **CustomerServiceLog** - 客服对话日志
- **CSVRegistry** - CSV 文件导入注册表

## 迁移步骤

### 方式 1: 一键迁移（推荐）

运行一键迁移脚本，自动完成所有步骤：

```bash
python -m backend.migrations.migrate_all
```

此命令会：
1. 创建 celebrity.db 和 customerService.db 的表结构
2. 自动从旧的 app.db 迁移数据（如果存在）
3. 备份旧数据库为 app.db.backup

### 方式 2: 分步迁移

#### 步骤 1: 创建新数据库表结构
```bash
python -m backend.migrations.add_celebrity_chunks
```

#### 步骤 2: 迁移旧数据（如果有旧数据库）
```bash
python -m backend.migrations.migrate_data_from_old_db
```

## 代码变更说明

### 数据库配置 (backend/core/database.py)

新增了两个独立的数据库引擎和会话工厂：

```python
# 数字名人数据库
celebrity_engine
celebrity_async_session()

# 数字客服数据库
customer_service_engine
customer_service_async_session()
```

### 模块修改

#### Celebrity 模块
所有文件已更新使用 `celebrity_async_session()`：
- `backend/apps/celebrity/app.py`
- `backend/apps/celebrity/services/celebrity_orchestrator.py`

#### Customer Service 模块
所有文件已更新使用 `customer_service_async_session()`：
- `backend/apps/customer_service/app.py`

## 验证迁移

迁移完成后，检查以下内容：

1. **数据库文件存在**
   ```
   backend/data/celebrity.db
   backend/data/customerService.db
   ```

2. **旧数据库备份**
   ```
   backend/data/app.db.backup (如果有旧数据)
   ```

3. **启动应用测试**
   ```bash
   uvicorn backend.main:app --reload
   ```

4. **功能测试**
   - 上传名人 PDF - 应存储到 celebrity.db
   - 导入客服 CSV - 应存储到 customerService.db
   - 名人对话 - 应从 celebrity.db 检索
   - 客服对话 - 应从 customerService.db 检索

## 清理旧数据库

迁移成功后，可以删除旧的 app.db：

```bash
# 删除旧数据库
rm backend/data/app.db

# 保留备份（可选）
# backend/data/app.db.backup
```

## 回滚方案

如果需要回滚到旧架构：

1. 停止应用
2. 恢复备份：`cp backend/data/app.db.backup backend/data/app.db`
3. 恢复旧版代码（使用 git）
4. 重启应用

## 注意事项

⚠️ **重要提醒**：
- 迁移前建议备份整个 backend/data 目录
- 首次运行迁移脚本时，如果没有旧数据库，会显示警告但不会报错
- 迁移是单向的，请确保在生产环境运行前充分测试
- 分离后的数据库各自独立，无法直接跨库查询

## 故障排除

### 问题 1: 找不到旧数据库
**现象**: 警告 "未找到旧数据库文件"
**解决**: 这是正常的，说明这是首次安装，无需迁移旧数据

### 问题 2: 导入错误
**现象**: `ImportError` 或 `ModuleNotFoundError`
**解决**: 确保在项目根目录运行迁移命令

### 问题 3: 表已存在
**现象**: 迁移时提示表已存在
**解决**: 删除新数据库后重新运行迁移脚本
```bash
rm backend/data/celebrity.db backend/data/customerService.db
python -m backend.migrations.migrate_all
```

## 技术细节

### 为什么要分离数据库？

1. **模块隔离** - 名人和客服是两个独立的业务模块
2. **便于维护** - 独立升级、备份、恢复
3. **性能优化** - 减少单一数据库的负载
4. **扩展性** - 未来可以迁移到不同的数据库服务器

### 兼容性保留

为保持向后兼容，`engine` 和 `async_session` 仍然可用，默认指向客服数据库。
