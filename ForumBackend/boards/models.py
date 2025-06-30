"""
板块模型
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Board(models.Model):
    """
    论坛板块模型
    """
    # 基本信息
    name = models.CharField('板块名称', max_length=100, unique=True)
    description = models.TextField('板块描述', blank=True)
    order = models.IntegerField('排序顺序', default=0, help_text='数字越小排序越靠前')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    # 权限控制
    ACCESS_CHOICES = (
        ('public', '公开'),
        ('registered', '仅注册用户'),
        ('groups', '指定用户组'),
        ('users', '指定用户')
    )
    access_type = models.CharField('访问权限类型', max_length=20, choices=ACCESS_CHOICES, default='public')
    allowed_groups = models.ManyToManyField(Group, verbose_name='允许访问的用户组', blank=True, related_name='accessible_boards')
    allowed_users = models.ManyToManyField(User, verbose_name='允许访问的用户', blank=True, related_name='accessible_boards')

    class Meta:
        verbose_name = '板块'
        verbose_name_plural = '板块'
        db_table = 'boards'
        ordering = ['order', 'id']  # 首先按order排序，然后按id排序

    def __str__(self):
        return self.name

    def can_access(self, user):
        """
        检查用户是否有权限访问该板块
        """
        # 公开板块，所有人都可以访问
        if self.access_type == 'public':
            return True

        # 仅注册用户可访问，检查用户是否已登录
        if self.access_type == 'registered':
            return user.is_authenticated

        # 如果用户是管理员，可以访问所有板块
        if user.is_authenticated and (user.is_superuser or getattr(user, 'is_admin', False) or getattr(user, 'role', '') == 'admin'):
            return True

        # 指定用户组可访问，检查用户是否在允许的用户组中
        if self.access_type == 'groups' and user.is_authenticated:
            # 检查用户是否有groups属性
            if hasattr(user, 'groups'):
                try:
                    user_groups = user.groups.all()
                    return self.allowed_groups.filter(id__in=[g.id for g in user_groups]).exists()
                except Exception:
                    # 如果获取用户组失败，默认没有权限
                    return False
            else:
                # 如果用户没有groups属性，默认没有权限
                return False

        # 指定用户可访问，检查用户是否在允许的用户列表中
        if self.access_type == 'users' and user.is_authenticated:
            return self.allowed_users.filter(id=user.id).exists()

        return False
