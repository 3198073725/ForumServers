"""
用户模型的管理后台配置
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    自定义用户管理后台
    """
    list_display = ('id', 'username', 'email', 'nickname', 'role', 'created_at', 'last_login')
    list_filter = ('role', 'created_at')
    search_fields = ('username', 'email', 'nickname')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('username', 'password_hash')}),
        (_('个人信息'), {'fields': ('email', 'nickname', 'avatar_url')}),
        (_('权限'), {'fields': ('role',)}),
        (_('重要日期'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')
