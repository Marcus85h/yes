import django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Swagger Schema 配置
schema_view = get_schema_view(
    openapi.Info(
        title="视频交友 API 文档",
        default_version="v1",
        description="视频交友应用 API 接口文档",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT 登录接口
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # 应用路由
    path("api/users/", include("apps.users.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/calls/", include("apps.calls.urls")),
    path("api/rooms/", include("apps.rooms.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/security/", include("apps.security.urls")),
    # API 文档（Swagger / Redoc）
    path(
        "api/docs/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]

# 静态文件（开发阶段）
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
