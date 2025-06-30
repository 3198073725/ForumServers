"""
用户头像上传视图
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import os
import uuid
from datetime import datetime

from .models import User
from forum_project.utils import success_response, error_response


class UserAvatarUploadView(APIView):
    """
    用户头像上传视图
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """上传用户头像"""
        if 'file' not in request.FILES:
            return error_response(msg="未提供头像文件")

        avatar_file = request.FILES['file']
        
        # 验证文件类型
        if not avatar_file.content_type.startswith('image/'):
            return error_response(msg="只能上传图片文件")
        
        # 验证文件大小（限制为2MB）
        if avatar_file.size > 2 * 1024 * 1024:
            return error_response(msg="头像文件大小不能超过2MB")
        
        # 创建保存头像的目录
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 生成唯一的文件名
        file_extension = os.path.splitext(avatar_file.name)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # 按日期组织文件
        today = datetime.now().strftime('%Y%m%d')
        date_dir = os.path.join(upload_dir, today)
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)
        
        # 保存文件
        file_path = os.path.join(date_dir, unique_filename)
        with open(file_path, 'wb+') as destination:
            for chunk in avatar_file.chunks():
                destination.write(chunk)
        
        # 生成可访问的URL
        avatar_url = f"{settings.MEDIA_URL}avatars/{today}/{unique_filename}"
        
        # 更新用户头像URL
        user = request.user
        user.avatar_url = avatar_url
        user.save(update_fields=['avatar_url'])
        
        return success_response({
            'avatar_url': avatar_url
        }, "头像上传成功")
