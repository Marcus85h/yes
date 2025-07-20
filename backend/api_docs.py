"""
API文档配置
"""

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# API文档视图
schema_view = get_schema_view(
    openapi.Info(
        title="视频交友应用 API",
        default_version="v1",
        description="""
        # 视频交友应用 API 文档
        
        ## 概述
        这是一个完整的视频交友应用后端API，提供用户管理、聊天、通话、房间等功能。
        
        ## 主要功能模块
        
        ### 用户管理
        - 用户注册、登录、认证
        - 用户资料管理
        - 实名认证
        
        ### 聊天系统
        - 私聊和群聊
        - 消息发送、接收、撤回
        - 文件上传和分享
        
        ### 视频通话
        - 一对一视频通话
        - 群组视频通话
        - 通话记录管理
        
        ### 房间系统
        - 房间创建和管理
        - 用户匹配
        - 房间评分
        
        ### 安全功能
        - 内容审核
        - 用户举报
        - 安全检测
        
        ## 认证方式
        使用JWT (JSON Web Token) 进行身份认证
        
        ## 响应格式
        所有API响应都使用统一的JSON格式
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# API标签定义
api_tags = [
    {"name": "认证", "description": "用户认证相关接口"},
    {"name": "用户", "description": "用户管理相关接口"},
    {"name": "聊天", "description": "聊天系统相关接口"},
    {"name": "通话", "description": "视频通话相关接口"},
    {"name": "房间", "description": "房间管理相关接口"},
    {"name": "安全", "description": "安全检测相关接口"},
    {"name": "支付", "description": "支付相关接口"},
    {"name": "管理", "description": "管理员相关接口"},
]

# 通用响应模式
responses = {
    "success": openapi.Response(
        description="成功响应",
        examples={"application/json": {"success": True, "message": "操作成功", "data": {}}},
    ),
    "error": openapi.Response(
        description="错误响应",
        examples={
            "application/json": {"success": False, "error": "错误信息", "code": "ERROR_CODE"}
        },
    ),
    "validation_error": openapi.Response(
        description="验证错误",
        examples={
            "application/json": {
                "success": False,
                "error": "验证失败",
                "errors": {"field_name": ["错误信息"]},
            }
        },
    ),
}

# 通用参数
common_parameters = [
    openapi.Parameter(
        "page", openapi.IN_QUERY, description="页码", type=openapi.TYPE_INTEGER, default=1
    ),
    openapi.Parameter(
        "page_size", openapi.IN_QUERY, description="每页数量", type=openapi.TYPE_INTEGER, default=20
    ),
    openapi.Parameter(
        "ordering", openapi.IN_QUERY, description="排序字段", type=openapi.TYPE_STRING
    ),
    openapi.Parameter(
        "search", openapi.IN_QUERY, description="搜索关键词", type=openapi.TYPE_STRING
    ),
]

# 认证参数
auth_parameters = [
    openapi.Parameter(
        "Authorization",
        openapi.IN_HEADER,
        description="JWT认证令牌",
        type=openapi.TYPE_STRING,
        format="Bearer <token>",
        required=True,
    )
]
