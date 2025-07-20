# 视频交友应用 - 后端

这是视频交友应用的Django后端服务，提供完整的REST API和WebSocket支持。

## 🚀 技术栈

- **框架**: Django 4.2.7 + Django REST Framework 3.14.0
- **数据库**: PostgreSQL
- **缓存**: Redis
- **认证**: JWT (JSON Web Tokens)
- **异步**: Django Channels (WebSocket)
- **任务队列**: Celery
- **文件存储**: AWS S3 / 本地存储
- **API文档**: Swagger/OpenAPI
- **监控**: Sentry
- **容器化**: Docker

## 📁 项目结构

```
backend/
├── apps/                    # 应用模块
│   ├── users/              # 用户管理
│   ├── rooms/              # 房间管理
│   ├── calls/              # 通话管理
│   ├── gifts/              # 礼物系统
│   ├── billing/            # 计费系统
│   ├── chat/               # 聊天系统
│   └── security/           # 安全模块
├── core/                   # 核心功能
├── video_dating/           # 项目配置
│   ├── settings/           # 环境设置
│   │   ├── base.py         # 基础设置
│   │   ├── development.py  # 开发环境
│   │   └── production.py   # 生产环境
│   ├── urls.py             # 主URL配置
│   ├── wsgi.py             # WSGI配置
│   └── asgi.py             # ASGI配置
├── requirements.txt        # Python依赖
├── Dockerfile              # Docker配置
├── manage.py               # Django管理脚本
└── test_backend.py         # 测试脚本
```

## 🛠️ 安装和运行

### 环境要求

- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- Node.js 16+ (用于前端)

### 1. 克隆项目

```bash
git clone <repository-url>
cd video-dating-app/backend
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 环境配置

复制环境变量文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库和其他服务：

```env
# Django设置
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=video_dating_dev
DB_USER=videodating
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 其他配置...
```

### 5. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 创建超级用户

```bash
python manage.py createsuperuser
```

### 7. 运行开发服务器

```bash
python manage.py runserver
```

## 🐳 Docker部署

### 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

### 单独构建后端镜像

```bash
# 构建镜像
docker build -t video-dating-backend .

# 运行容器
docker run -p 8000:8000 video-dating-backend
```

## 📚 API文档

启动服务器后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

## 🔧 开发指南

### 代码规范

- 遵循PEP 8 Python代码规范
- 使用类型提示
- 编写单元测试
- 添加适当的文档字符串

### 测试

运行测试：

```bash
# 运行所有测试
python manage.py test

# 运行特定应用的测试
python manage.py test apps.users

# 运行测试脚本
python test_backend.py
```

### 代码检查

```bash
# 代码格式检查
flake8 .

# 类型检查
mypy .

# 安全检查
bandit -r .
```

## 📊 监控和日志

### 日志配置

日志文件位置：`logs/app.log`

### 健康检查

访问 `/health/` 端点检查服务状态：

```bash
curl http://localhost:8000/health/
```

### 性能监控

- 使用Django Debug Toolbar (开发环境)
- 集成Sentry进行错误监控
- 使用Prometheus + Grafana进行指标监控

## 🔐 安全配置

### 认证和授权

- JWT令牌认证
- 基于角色的权限控制
- 登录失败限制 (Django Axes)

### 数据保护

- 密码加密存储
- 敏感数据脱敏
- HTTPS强制重定向 (生产环境)

### API安全

- CORS配置
- 请求频率限制
- 输入验证和清理

## 🚀 部署

### 生产环境部署

1. 设置生产环境变量
2. 配置数据库和Redis
3. 收集静态文件
4. 配置Web服务器 (Nginx)
5. 使用Gunicorn运行应用

### 环境变量

生产环境需要配置以下环境变量：

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
SENTRY_DSN=your-sentry-dsn
```

## 📝 主要功能

### 用户管理
- 用户注册/登录
- 用户资料管理
- 实名认证
- 设备管理

### 房间系统
- 房间创建和管理
- 用户匹配
- 在线状态管理

### 视频通话
- WebRTC集成
- 通话记录
- 通话质量监控

### 礼物系统
- 礼物购买和发送
- 礼物排行榜
- 收益统计

### 计费系统
- 充值功能
- 消费记录
- 支付集成

### 聊天系统
- 实时消息
- 消息历史
- 表情和图片支持

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目地址: [GitHub Repository URL] 