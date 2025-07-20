# 视频交友APP启动指南

## 🚀 快速开始

### 环境要求

#### 开发环境
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Flutter**: 3.16.0+
- **Python**: 3.11+
- **Node.js**: 18+ (可选，用于前端开发工具)

#### 生产环境
- **服务器**: AWS EC2, Google Cloud Compute, 阿里云ECS
- **容器编排**: Kubernetes 1.24+
- **数据库**: PostgreSQL 15+
- **缓存**: Redis 7+
- **存储**: AWS S3, 阿里云OSS

### 1. 克隆项目

```bash
# 克隆项目
git clone https://github.com/your-username/video-dating-app.git
cd video-dating-app

# 切换到开发分支
git checkout develop
```

### 2. 环境配置

#### 2.1 复制环境变量文件

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑环境变量
nano .env
```

#### 2.2 配置关键环境变量

```bash
# 应用配置
DEBUG=True
SECRET_KEY=your-development-secret-key

# 数据库配置
DB_NAME=video_dating_dev
DB_USER=videodating
DB_PASSWORD=your-db-password
DB_HOST=postgres
DB_PORT=5432

# Redis配置
REDIS_URL=redis://:your-redis-password@redis:6379/0
REDIS_PASSWORD=your-redis-password

# 文件存储配置（开发环境）
AWS_ACCESS_KEY_ID=dev
AWS_SECRET_ACCESS_KEY=dev
AWS_STORAGE_BUCKET_NAME=dev-bucket
AWS_S3_REGION_NAME=us-east-1
```

### 3. 启动开发环境

#### 3.1 使用快速启动脚本（推荐）

```bash
# 给脚本执行权限
chmod +x scripts/quick-start.sh

# 运行快速启动脚本
./scripts/quick-start.sh
```

#### 3.2 手动启动

```bash
# 启动基础服务
docker-compose up -d postgres redis

# 等待数据库启动
sleep 10

# 启动后端服务
docker-compose up -d backend

# 运行数据库迁移
docker-compose exec backend python manage.py migrate

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser

# 启动其他服务
docker-compose up -d websocket webrtc
```

### 4. 启动前端

#### 4.1 安装Flutter依赖

```bash
cd frontend
flutter pub get
```

#### 4.2 运行Flutter应用

```bash
# 检查可用设备
flutter devices

# 运行应用
flutter run
```

### 5. 验证安装

#### 5.1 检查服务状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f backend
```

#### 5.2 访问服务

- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs/
- **管理后台**: http://localhost:8000/admin/
- **WebSocket**: ws://localhost:8001
- **WebRTC**: ws://localhost:8002

#### 5.3 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health/

# 检查WebSocket服务
curl http://localhost:8001/health/

# 检查WebRTC服务
curl http://localhost:8002/health/
```

## 🔧 开发指南

### 项目结构

```
video-dating-app/
├── frontend/                 # Flutter前端应用
├── backend/                  # Django后端应用
├── websocket_service/        # WebSocket服务
├── webrtc_service/          # WebRTC服务
├── docker/                  # Docker配置
├── scripts/                 # 部署脚本
├── docs/                    # 文档
├── docker-compose.yml       # Docker Compose配置
├── env.example              # 环境变量示例
└── README.md               # 项目说明
```

### 开发工作流

#### 1. 后端开发

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行测试
python manage.py test

# 创建新的应用
python manage.py startapp new_app

# 创建数据库迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate
```

#### 2. 前端开发

```bash
cd frontend

# 运行测试
flutter test

# 代码分析
flutter analyze

# 构建APK
flutter build apk

# 构建iOS
flutter build ios
```

#### 3. 数据库管理

```bash
# 进入数据库
docker-compose exec postgres psql -U videodating -d video_dating_dev

# 备份数据库
docker-compose exec postgres pg_dump -U videodating video_dating_dev > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U videodating -d video_dating_dev < backup.sql
```

### 调试技巧

#### 1. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f websocket
docker-compose logs -f webrtc

# 查看Flutter日志
flutter logs
```

#### 2. 调试WebRTC

```bash
# 检查WebRTC连接
docker-compose exec webrtc python -c "
import asyncio
from webrtc_service.main import app
print('WebRTC服务状态:', app.state)
"
```

#### 3. 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看数据库性能
docker-compose exec postgres psql -U videodating -d video_dating_dev -c "
SELECT * FROM pg_stat_activity;
"
```

## 🚀 部署指南

### 开发环境部署

```bash
# 使用快速启动脚本
./scripts/quick-start.sh
```

### 测试环境部署

```bash
# 部署到测试环境
./scripts/deploy.sh staging
```

### 生产环境部署

```bash
# 部署到生产环境
./scripts/deploy.sh production
```

### 使用Docker Compose部署

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

## 📊 监控和日志

### 访问监控面板

- **Grafana**: http://localhost:3000 (admin/admin)
- **Kibana**: http://localhost:5601
- **Prometheus**: http://localhost:9090

### 查看应用日志

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看访问日志
tail -f logs/access.log
```

## 🔒 安全配置

### 1. 生产环境安全

```bash
# 生成强密钥
python -c "import secrets; print(secrets.token_urlsafe(50))"

# 配置SSL证书
# 将证书文件放在 ssl/ 目录下
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem
```

### 2. 数据库安全

```bash
# 创建只读用户
docker-compose exec postgres psql -U videodating -d video_dating_dev -c "
CREATE USER readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE video_dating_dev TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
"
```

### 3. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## 🐛 故障排除

### 常见问题

#### 1. 数据库连接失败

```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U videodating

# 重启数据库
docker-compose restart postgres
```

#### 2. Redis连接失败

```bash
# 检查Redis状态
docker-compose exec redis redis-cli ping

# 重启Redis
docker-compose restart redis
```

#### 3. WebRTC连接问题

```bash
# 检查STUN/TURN服务器
curl -I https://stun.l.google.com:19302

# 查看WebRTC日志
docker-compose logs -f webrtc
```

#### 4. Flutter构建失败

```bash
# 清理缓存
flutter clean
flutter pub get

# 检查Flutter版本
flutter --version

# 更新Flutter
flutter upgrade
```

### 性能优化

#### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_rooms_status ON rooms(status);
CREATE INDEX idx_call_sessions_start_time ON call_sessions(start_time);

-- 分析表
ANALYZE users;
ANALYZE rooms;
ANALYZE call_sessions;
```

#### 2. Redis优化

```bash
# 配置Redis内存
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### 3. 应用优化

```bash
# 启用Gunicorn多进程
docker-compose exec backend gunicorn --workers 4 --bind 0.0.0.0:8000 video_dating.wsgi:application
```

## 📚 学习资源

### 官方文档
- [Flutter官方文档](https://flutter.dev/docs)
- [Django官方文档](https://docs.djangoproject.com/)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [WebRTC官方文档](https://webrtc.org/)

### 视频教程
- [Flutter视频通话开发](https://www.youtube.com/watch?v=example)
- [Django REST API开发](https://www.youtube.com/watch?v=example)
- [WebRTC实战教程](https://www.youtube.com/watch?v=example)

### 社区资源
- [Flutter社区](https://flutter.dev/community)
- [Django社区](https://www.djangoproject.com/community/)
- [Stack Overflow](https://stackoverflow.com/)

## 🤝 贡献指南

### 开发流程

1. **Fork项目**
2. **创建功能分支**: `git checkout -b feature/your-feature`
3. **提交代码**: `git commit -m 'Add your feature'`
4. **推送分支**: `git push origin feature/your-feature`
5. **创建Pull Request**

### 代码规范

- **Python**: 遵循PEP 8规范
- **Flutter**: 遵循Flutter官方代码规范
- **Git**: 使用Conventional Commits
- **API**: 遵循RESTful设计原则

### 测试要求

```bash
# 运行所有测试
python manage.py test
flutter test

# 代码覆盖率
coverage run --source='.' manage.py test
coverage report
```

## 📞 技术支持

### 联系方式
- **邮箱**: support@videodating.com
- **微信**: videodating_support
- **QQ群**: 123456789

### 问题反馈
- [GitHub Issues](https://github.com/your-username/video-dating-app/issues)
- [Discord社区](https://discord.gg/videodating)

---

**注意**: 这是一个完整的生产级应用启动指南。在实际使用前，请确保所有安全措施和合规要求都已满足。 