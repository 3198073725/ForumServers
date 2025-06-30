"""
自定义认证后端
"""

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User


class CustomAuthBackend(ModelBackend):
    """
    自定义认证后端，支持使用用户名或邮箱登录，并使用password_hash字段验证密码
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        使用用户名或邮箱和密码进行认证
        """
        if username is None or password is None:
            return None
        
        try:
            # 查找用户（支持用户名或邮箱）
            user = User.objects.get(Q(username=username) | Q(email=username))
            
            # 验证密码
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # 运行默认的密码哈希算法以防止时间攻击
            User().set_password(password)
            return None
        
        return None
