"""
评论相关URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
