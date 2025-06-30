"""
用户头像上传相关URL配置
"""

from django.urls import path
from users.views_avatar import UserAvatarUploadView

urlpatterns = [
    # 头像上传
    path('profile/me/avatar/', UserAvatarUploadView.as_view(), name='user_avatar_upload'),
]
