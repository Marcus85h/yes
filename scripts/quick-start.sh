#!/bin/bash

# 视频交友APP快速启动脚本（开发环境）
# 使用方法: ./scripts/quick-start.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "🚀 视频交友APP快速启动脚本"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查Flutter是否安装
if ! command -v flutter &> /dev/null; then
    log_warning "Flutter未安装，将跳过前端启动"
    FLUTTER_AVAILABLE=false
else
    FLUTTER_AVAILABLE=true
    log_info "检测到Flutter: $(flutter --version | head -n 1)"
fi

# 创建环境变量文件
if [ ! -f ".env" ]; then
    log_info "创建开发环境变量文件..."
    cat > .env << EOF
# 开发环境配置
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=video_dating_dev
DB_USER=videodating
DB_PASSWORD=dev_password
DB_HOST=postgres
DB_PORT=5432

# Redis配置
REDIS_URL=redis://:dev_redis_password@redis:6379/0
REDIS_PASSWORD=dev_redis_password

# 文件存储配置（开发环境使用本地存储）
AWS_ACCESS_KEY_ID=dev
AWS_SECRET_ACCESS_KEY=dev
AWS_STORAGE_BUCKET_NAME=dev-bucket
AWS_S3_REGION_NAME=us-east-1

# WebRTC配置
STUN_SERVERS=stun:stun.l.google.com:19302
TURN_SERVERS=

# 功能开关
ENABLE_VIDEO_CALL=True
ENABLE_AUDIO_CALL=True
ENABLE_GIFT_SYSTEM=True
ENABLE_PAYMENT=False
ENABLE_PUSH_NOTIFICATION=False
ENABLE_THIRD_PARTY_LOGIN=False
ENABLE_SCREEN_RECORDING=False

# 日志配置
LOG_LEVEL=DEBUG
EOF
    log_success "环境变量文件创建完成"
fi

# 创建前端环境变量文件
if [ ! -f "frontend/.env.dart" ]; then
    log_info "创建前端环境变量文件 frontend/.env.dart..."
    cat > frontend/.env.dart << EOF
/// 自动生成的前端环境变量文件（开发环境）
class Env {
  static const String baseUrl = 'http://localhost:8000';
  static const String wsUrl = 'ws://localhost:8001';
  static const String webrtcUrl = 'ws://localhost:8002';
  static const bool enableVideoCall = true;
  static const bool enableAudioCall = true;
  static const bool enableGiftSystem = true;
  static const bool enablePayment = false;
  static const bool enablePushNotification = false;
  static const bool enableThirdPartyLogin = false;
  static const bool enableScreenRecording = false;
  static const bool isProduction = false;
  static const bool isDebug = true;
}
EOF
    log_success "前端环境变量文件创建完成"
fi

# 创建必要的目录
log_info "创建必要的目录..."
mkdir -p logs
mkdir -p backup
mkdir -p frontend/assets/images
mkdir -p frontend/assets/icons
mkdir -p frontend/assets/animations
mkdir -p frontend/assets/sounds
mkdir -p frontend/assets/fonts

# 端口占用检测函数
check_port() {
    local port=$1
    if lsof -i :$port &>/dev/null; then
        log_error "端口 $port 已被占用，请释放后再运行本脚本。"
        exit 1
    fi
}

# 检查常用端口
log_info "检查常用端口占用情况..."
check_port 8000
check_port 8001
check_port 8002

# 启动后端服务
log_info "启动后端服务..."
docker-compose up -d postgres redis

# 等待数据库启动
log_info "等待数据库启动..."
sleep 10

# 检查数据库连接
if docker-compose exec postgres pg_isready -U videodating -d video_dating_dev; then
    log_success "数据库连接正常"
else
    log_error "数据库连接失败"
    exit 1
fi

# 启动后端应用
log_info "启动后端应用..."
docker-compose up -d backend

# 等待后端启动
log_info "等待后端启动..."
sleep 15

# 运行数据库迁移
log_info "运行数据库迁移..."
docker-compose exec backend python manage.py migrate --noinput

# 创建超级用户
log_info "创建超级用户..."
docker-compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户创建成功: admin/admin123')
else:
    print('超级用户已存在')
"

# 收集静态文件
log_info "收集静态文件..."
docker-compose exec backend python manage.py collectstatic --noinput

# 启动其他服务
log_info "启动其他服务..."
docker-compose up -d websocket webrtc

# 检查服务状态
log_info "检查服务状态..."
services=("postgres" "redis" "backend" "websocket" "webrtc")

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        log_success "$service 服务运行正常"
    else
        log_error "$service 服务启动失败"
        docker-compose logs "$service"
    fi
done

# 启动前端（如果Flutter可用）
if [ "$FLUTTER_AVAILABLE" = true ]; then
    log_info "启动Flutter前端..."
    cd frontend
    
    # 安装依赖
    log_info "安装Flutter依赖..."
    flutter pub get
    
    # 检查设备
    log_info "检查可用设备..."
    flutter devices
    
    # 启动应用
    log_info "启动Flutter应用..."
    echo "请选择要运行的设备:"
    echo "1. Android模拟器"
    echo "2. iOS模拟器"
    echo "3. Web浏览器"
    echo "4. 连接的真机设备"
    read -p "请输入选择 (1-4): " choice
    
    case $choice in
        1)
            flutter run -d android
            ;;
        2)
            flutter run -d ios
            ;;
        3)
            flutter run -d chrome
            ;;
        4)
            flutter run
            ;;
        *)
            log_warning "无效选择，使用默认设备"
            flutter run
            ;;
    esac
    
    cd ..
else
    log_warning "Flutter未安装，跳过前端启动"
fi

# 显示访问信息
log_success "🎉 开发环境启动完成！"
echo ""
echo "📱 服务访问地址:"
echo "  - 后端API: http://localhost:8000"
echo "  - API文档: http://localhost:8000/api/docs/"
echo "  - 管理后台: http://localhost:8000/admin/"
echo "  - WebSocket: ws://localhost:8001"
echo "  - WebRTC: ws://localhost:8002"
echo ""
echo "🔑 管理员账号:"
echo "  - 用户名: admin"
echo "  - 密码: admin123"
echo ""
echo "📋 常用命令:"
echo "  - 查看日志: docker-compose logs -f [服务名]"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart [服务名]"
echo "  - 进入容器: docker-compose exec [服务名] bash"
echo ""
echo "🚀 开始开发吧！" 

# 多语言支持信息
echo ""
echo "🌍 多语言支持:"
echo "  - 简体中文 (zh-CN) - 默认"
echo "  - 繁体中文 (zh-TW)"
echo "  - 英语 (en)"
echo "  - 西班牙语 (es)"
echo "  - 法语 (fr)"
echo "  - 拉丁语 (la)"
echo "  - 德语 (de)"
echo "  - 阿拉伯语 (ar)"
echo "  - 越南文 (vi)"
echo "  - 泰文 (th)"
echo "  - 日文 (ja)"
echo "  - 韩文 (ko)"
echo "  - 支持自动翻译功能"
echo "  - 语言设置: 我的 -> 语言设置"
echo ""
echo "📝 国际化使用说明:"
echo "  - 文本翻译: 'key'.tr()"
echo "  - 参数翻译: 'key'.tr(args: ['param'])"
echo "  - 复数翻译: 'key'.tr(n: count)"
echo "  - 语言切换: LocalizationService.instance.changeLanguage()"
echo "" 