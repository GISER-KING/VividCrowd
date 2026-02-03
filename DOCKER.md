# VividCrowd Docker 部署说明

## 快速启动

### 1. 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
nano .env
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看服务状态
docker-compose ps
```

### 4. 访问应用

- 前端：http://localhost
- 后端 API 文档：http://localhost:8000/docs

### 5. 停止服务

```bash
# 停止服务
docker-compose down

# 停止服务并删除数据卷
docker-compose down -v
```

## 常用命令

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启后端服务
docker-compose restart backend

# 重启前端服务
docker-compose restart frontend
```

### 重新构建

```bash
# 重新构建并启动
docker-compose up -d --build

# 仅重新构建后端
docker-compose build backend

# 仅重新构建前端
docker-compose build frontend
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh
```

### 查看资源使用

```bash
# 查看容器资源使用情况
docker stats

# 查看磁盘使用
docker system df
```

## 数据持久化

数据库文件和日志文件通过 Docker 卷持久化：

- `./backend/data` - 数据库文件
- `./backend/logs` - 日志文件

即使删除容器，这些数据也会保留。

## 生产环境部署

### 1. 使用自定义端口

编辑 `docker-compose.yml`：

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 修改为自定义端口
```

### 2. 配置 HTTPS

使用 Nginx 反向代理：

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 资源限制

编辑 `docker-compose.yml` 添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 4. 自动重启策略

```yaml
services:
  backend:
    restart: always  # 总是重启
    # 或
    restart: on-failure  # 仅失败时重启
```

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 检查容器状态
docker-compose ps

# 检查健康状态
docker inspect vividcrowd-backend | grep Health
```

### 网络连接问题

```bash
# 检查网络
docker network ls
docker network inspect vividcrowd-network

# 测试容器间连接
docker-compose exec frontend ping backend
```

### 数据库文件权限问题

```bash
# 修复权限
sudo chown -R 1000:1000 backend/data
sudo chmod -R 755 backend/data
```

## 备份与恢复

### 备份数据

```bash
# 备份数据库文件
tar -czf backup-$(date +%Y%m%d).tar.gz backend/data

# 或使用 Docker 卷备份
docker run --rm -v vividcrowd-backend-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/data-backup.tar.gz /data
```

### 恢复数据

```bash
# 解压备份文件
tar -xzf backup-20260204.tar.gz

# 或从 Docker 卷恢复
docker run --rm -v vividcrowd-backend-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/data-backup.tar.gz -C /
```

## 更新应用

```bash
# 1. 拉取最新代码
git pull

# 2. 停止服务
docker-compose down

# 3. 重新构建
docker-compose build

# 4. 启动服务
docker-compose up -d

# 5. 查看日志确认启动成功
docker-compose logs -f
```

## 性能优化

### 1. 使用多阶段构建

前端 Dockerfile 已使用多阶段构建，减小镜像体积。

### 2. 使用 .dockerignore

创建 `.dockerignore` 文件：

```
node_modules
.git
.env
*.log
__pycache__
*.pyc
.venv
venv
```

### 3. 镜像缓存

```bash
# 使用 BuildKit 加速构建
DOCKER_BUILDKIT=1 docker-compose build
```

## 监控

### 使用 Docker Stats

```bash
# 实时监控
docker stats vividcrowd-backend vividcrowd-frontend
```

### 集成 Prometheus

添加到 `docker-compose.yml`：

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## 安全建议

1. **不要在镜像中硬编码密钥**
2. **使用 Docker secrets 管理敏感信息**
3. **定期更新基础镜像**
4. **扫描镜像漏洞**：`docker scan vividcrowd-backend`
5. **限制容器权限**：避免使用 `privileged` 模式
