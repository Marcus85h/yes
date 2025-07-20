"""
核心应用URL配置
"""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.health_check, name="health_check"),
    path("info/", views.api_info, name="api_info"),
]
