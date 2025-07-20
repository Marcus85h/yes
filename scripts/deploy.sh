#!/bin/bash

# 视频交友APP部署脚本
# 支持开发、测试、生产环境部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 配置变量
ENVIRONMENT=${1:-development}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"your-registry.com"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
BACKUP_ENABLED=${BACKUP_ENABLED:-true}
HEALTH_CHECK_ENABLED=${HEALTH_CHECK_ENABLED:-true}

# 显示部署信息
log_info "🚀 开始部署视频交友APP"
log_info "环境: $ENVIRONMENT"
log_info "Docker镜像: $DOCKER_REGISTRY/video-dating:$IMAGE_TAG"

# 检查必要工具
check_requirements() {
    log_info "检查部署环境..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装"
        exit 1
    fi
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        log_error "Git未安装"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 备份数据库
backup_database() {
    if [ "$BACKUP_ENABLED" = true ]; then
        log_info "备份数据库..."
        
        BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # PostgreSQL备份
        docker-compose exec -T postgres pg_dump -U videodating -d video_dating_dev > "$BACKUP_DIR/database.sql"
        
        # Redis备份
        docker-compose exec -T redis redis-cli SAVE
        docker cp $(docker-compose ps -q redis):/data/dump.rdb "$BACKUP_DIR/redis.rdb"
        
        # 压缩备份文件
        tar -czf "$BACKUP_DIR.tar.gz" -C backup "$(basename $BACKUP_DIR)"
        rm -rf "$BACKUP_DIR"
        
        log_success "数据库备份完成: $BACKUP_DIR.tar.gz"
    fi
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建后端镜像
    docker build -t $DOCKER_REGISTRY/video-dating-backend:$IMAGE_TAG ./backend
    
    # 构建前端镜像
    docker build -t $DOCKER_REGISTRY/video-dating-frontend:$IMAGE_TAG ./frontend
    
    # 推送镜像到仓库
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "推送镜像到仓库..."
        docker push $DOCKER_REGISTRY/video-dating-backend:$IMAGE_TAG
        docker push $DOCKER_REGISTRY/video-dating-frontend:$IMAGE_TAG
    fi
    
    log_success "镜像构建完成"
}

# 运行测试
run_tests() {
    log_info "运行测试套件..."
    
    # 后端测试
    docker-compose exec backend python manage.py test --verbosity=2 --parallel
    
    # 前端测试
    cd frontend
    flutter test
    
    # 集成测试
    docker-compose exec backend python manage.py test tests.integration --verbosity=2
    
    log_success "测试通过"
}

# 代码质量检查
code_quality_check() {
    log_info "代码质量检查..."
    
    # Python代码检查
    docker-compose exec backend black --check .
    docker-compose exec backend isort --check-only .
    docker-compose exec backend flake8 .
    docker-compose exec backend mypy .
    
    # 安全检查
    docker-compose exec backend bandit -r .
    docker-compose exec backend safety check
    
    # Flutter代码检查
    cd frontend
    flutter analyze
    
    log_success "代码质量检查通过"
}

# 数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    docker-compose exec backend python manage.py migrate --noinput
    
    log_success "数据库迁移完成"
}

# 收集静态文件
collect_static() {
    log_info "收集静态文件..."
    
    docker-compose exec backend python manage.py collectstatic --noinput
    
    log_success "静态文件收集完成"
}

# 健康检查
health_check() {
    if [ "$HEALTH_CHECK_ENABLED" = true ]; then
        log_info "执行健康检查..."
        
        # 等待服务启动
        sleep 30
        
        # 检查后端API
        if curl -f http://localhost:8000/api/health/; then
            log_success "后端API健康检查通过"
        else
            log_error "后端API健康检查失败"
            exit 1
        fi
        
        # 检查数据库连接
        if docker-compose exec backend python manage.py check --database default; then
            log_success "数据库连接检查通过"
        else
            log_error "数据库连接检查失败"
            exit 1
        fi
        
        # 检查Redis连接
        if docker-compose exec redis redis-cli ping | grep -q PONG; then
            log_success "Redis连接检查通过"
        else
            log_error "Redis连接检查失败"
            exit 1
        fi
        
        log_success "所有健康检查通过"
    fi
}

# 性能测试
performance_test() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "执行性能测试..."
        
        # 使用Apache Bench进行压力测试
        ab -n 1000 -c 10 http://localhost:8000/api/health/
        
        # 检查响应时间
        RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:8000/api/health/)
        if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
            log_success "性能测试通过，响应时间: ${RESPONSE_TIME}s"
        else
            log_warning "响应时间较慢: ${RESPONSE_TIME}s"
        fi
    fi
}

# 部署应用
deploy_application() {
    log_info "部署应用到 $ENVIRONMENT 环境..."
    
    # 停止现有服务
    docker-compose down
    
    # 启动服务
    docker-compose up -d
    
    # 等待服务启动
    sleep 10
    
    log_success "应用部署完成"
}

# 清理资源
cleanup() {
    log_info "清理资源..."
    
    # 清理未使用的Docker镜像
    docker image prune -f
    
    # 清理未使用的容器
    docker container prune -f
    
    # 清理未使用的网络
    docker network prune -f
    
    log_success "资源清理完成"
}

# 监控部署
monitor_deployment() {
    log_info "监控部署状态..."
    
    # 检查服务状态
    docker-compose ps
    
    # 检查日志
    docker-compose logs --tail=50
    
    # 检查资源使用情况
    docker stats --no-stream
    
    log_success "部署监控完成"
}

# 回滚部署
rollback() {
    log_error "部署失败，开始回滚..."
    
    # 停止服务
    docker-compose down
    
    # 恢复数据库备份
    if [ -f "backup/latest_backup.tar.gz" ]; then
        log_info "恢复数据库备份..."
        tar -xzf backup/latest_backup.tar.gz
        docker-compose exec -T postgres psql -U videodating -d video_dating_dev < backup/database.sql
    fi
    
    # 使用上一个版本的镜像
    docker-compose up -d
    
    log_warning "回滚完成"
}

# 主部署流程
main() {
    case $ENVIRONMENT in
        "development")
            log_info "部署到开发环境"
            check_requirements
            build_images
            run_tests
            code_quality_check
            deploy_application
            health_check
            ;;
        "testing")
            log_info "部署到测试环境"
            check_requirements
            backup_database
            build_images
            run_tests
            code_quality_check
            deploy_application
            health_check
            performance_test
            ;;
        "production")
            log_info "部署到生产环境"
            check_requirements
            backup_database
            build_images
            run_tests
            code_quality_check
            deploy_application
            health_check
            performance_test
            monitor_deployment
            ;;
        *)
            log_error "未知环境: $ENVIRONMENT"
            echo "用法: $0 [development|testing|production]"
            exit 1
            ;;
    esac
    
    cleanup
    
    log_success "🎉 部署完成！"
    
    # 显示访问信息
    echo ""
    echo "📱 服务访问地址:"
    echo "  - 后端API: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/api/docs/"
    echo "  - 管理后台: http://localhost:8000/admin/"
    echo "  - 前端应用: http://localhost:3000"
    echo ""
    echo "🔧 管理命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 停止服务: docker-compose down"
    echo "  - 更新代码: git pull && $0 $ENVIRONMENT"
}

# 错误处理
trap 'rollback' ERR

# 执行主流程
main "$@" 