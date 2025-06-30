"""
用户模型定义
"""

import random
import string
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings


class UserManager(BaseUserManager):
    """
    自定义用户管理器
    """
    def create_user(self, username, email, password=None, **extra_fields):
        """
        创建普通用户
        """
        if not username:
            raise ValueError('用户名不能为空')
        if not email:
            raise ValueError('邮箱不能为空')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            # 直接设置password_hash字段
            user.password_hash = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        创建超级用户
        """
        extra_fields.setdefault('role', 'admin')
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser):
    """
    自定义用户模型 - 直接匹配数据库表结构
    """
    ROLE_CHOICES = (
        ('guest', '访客'),
        ('user', '普通用户'),
        ('moderator', '版主'),
        ('admin', '管理员'),
    )

    id = models.BigAutoField(primary_key=True)
    username = models.CharField('用户名', max_length=50, unique=True)
    email = models.EmailField('邮箱', max_length=100, unique=True)
    # 密码字段重命名为password_hash
    password_hash = models.CharField('密码', max_length=255)
    nickname = models.CharField('昵称', max_length=50, blank=True, null=True)
    avatar_url = models.CharField('头像URL', max_length=255, blank=True, null=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='user')
    is_superuser = models.BooleanField('是否超级用户', default=False)
    created_at = models.DateTimeField('注册时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    last_login = models.DateTimeField('最后登录时间', blank=True, null=True)

    # 覆盖AbstractBaseUser的password字段
    password = None

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'users'
        managed = False  # 表示该模型不由Django管理，而是使用现有的数据库表

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.nickname or self.username

    def get_short_name(self):
        return self.username

    # 覆盖AbstractBaseUser的方法，使用password_hash字段
    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    @property
    def is_moderator(self):
        return self.role in ['moderator', 'admin']

    @property
    def is_admin(self):
        return self.role == 'admin'

    # 权限相关方法
    def has_perm(self, perm, obj=None):
        # 管理员有所有权限
        return self.role == 'admin'

    def has_module_perms(self, app_label):
        # 管理员有所有模块权限
        return self.role == 'admin'

    # 为了兼容Django admin，添加is_staff和is_active属性
    @property
    def is_staff(self):
        return self.role == 'admin'

    @property
    def is_active(self):
        return True


class VerificationCode(models.Model):
    """
    验证码模型
    """
    TYPE_CHOICES = (
        ('register', '注册'),
        ('reset_password', '重置密码'),
    )

    email = models.EmailField('邮箱')
    code = models.CharField('验证码', max_length=6)
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    expires_at = models.DateTimeField('过期时间')
    is_used = models.BooleanField('是否已使用', default=False)

    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        db_table = 'verification_codes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.code} - {self.type}"

    @classmethod
    def generate_code(cls, email, type):
        """
        生成验证码
        """
        # 生成随机6位数字验证码
        code = ''.join(random.choices(string.digits, k=6))

        # 计算过期时间
        expires_at = timezone.now() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)

        # 失效该邮箱的所有同类型未使用的验证码
        cls.objects.filter(
            email=email,
            type=type,
            is_used=False
        ).update(is_used=True)

        # 创建新验证码
        verification_code = cls.objects.create(
            email=email,
            code=code,
            type=type,
            expires_at=expires_at
        )

        return verification_code

    @classmethod
    def verify_code(cls, email, code, type, mark_used=True):
        """
        验证验证码

        Args:
            email: 邮箱
            code: 验证码
            type: 验证码类型
            mark_used: 是否标记为已使用，默认为True
        """
        try:
            # 查找未使用的验证码
            verification_code = cls.objects.get(
                email=email,
                code=code,
                type=type,
                is_used=False,
                expires_at__gt=timezone.now()
            )

            # 标记为已使用（如果需要）
            if mark_used:
                verification_code.is_used = True
                verification_code.save(update_fields=['is_used'])

            return True
        except cls.DoesNotExist:
            return False
