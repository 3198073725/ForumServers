"""
板块相关URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BoardViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'', BoardViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
