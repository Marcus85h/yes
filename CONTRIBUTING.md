# 贡献指南

感谢您对视频交友APP项目的关注！我们欢迎所有形式的贡献。

## 如何贡献

### 报告Bug
如果您发现了一个bug，请使用我们的[bug报告模板](.github/ISSUE_TEMPLATE/bug_report.md)创建一个issue。

### 请求功能
如果您有一个功能建议，请使用我们的[功能请求模板](.github/ISSUE_TEMPLATE/feature_request.md)创建一个issue。

### 提交代码
1. Fork这个仓库
2. 创建一个功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个Pull Request

## 开发环境设置

### 后端开发
```bash
# 克隆仓库
git clone https://github.com/your-username/video-dating-app.git
cd video-dating-app

# 设置Python环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r backend/requirements.txt

# 设置环境变量
cp env.example .env
# 编辑.env文件

# 运行数据库迁移
cd backend
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

### 前端开发
```bash
# 进入前端目录
cd frontend

# 安装Flutter依赖
flutter pub get

# 运行应用
flutter run
```

## 代码规范

### Python (后端)
- 遵循PEP 8规范
- 使用Black进行代码格式化
- 使用isort进行导入排序
- 使用flake8进行代码检查
- 使用mypy进行类型检查

```bash
# 格式化代码
black .
isort .

# 检查代码质量
flake8 .
mypy .
```

### Dart/Flutter (前端)
- 遵循Dart官方代码规范
- 使用flutter analyze检查代码
- 使用flutter format格式化代码

```bash
# 格式化代码
flutter format .

# 检查代码质量
flutter analyze
```

## 测试

### 后端测试
```bash
cd backend
python manage.py test
```

### 前端测试
```bash
cd frontend
flutter test
```

## 提交信息规范

我们使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

- `feat:` 新功能
- `fix:` Bug修复
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat: 添加用户注册功能
fix: 修复视频通话连接问题
docs: 更新API文档
```

## 行为准则

请参阅我们的[行为准则](CODE_OF_CONDUCT.md)以了解我们社区的期望。

## 许可证

通过贡献，您同意您的贡献将在MIT许可证下发布。

## 联系方式

如果您有任何问题，请通过以下方式联系我们：
- 邮箱: support@videodating.com
- 微信: videodating_support
- QQ群: 123456789

感谢您的贡献！ 