"""
用户信息相关URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (
    UserProfileView,
    PasswordChangeView,
    UserProfileViewSet
)

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'profile', UserProfileViewSet)

urlpatterns = [
    # 当前用户信息 - 旧版本，保留兼容性
    path('me/', UserProfileView.as_view(), name='user_profile'),

    # 修改密码
    path('me/password/', PasswordChangeView.as_view(), name='password_change'),

    # 用户个人中心相关路由
    path('', include(router.urls)),

    # 头像上传相关路由
    path('', include('users.urls.avatar')),
]
