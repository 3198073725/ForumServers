"""
自定义权限类
"""

from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    仅管理员可以修改，其他用户只读
    """
    
    def has_permission(self, request, view):
        # 允许所有用户进行GET, HEAD, OPTIONS请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 仅管理员可以进行其他请求
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsAuthorOrModeratorOrReadOnly(permissions.BasePermission):
    """
    作者或版主可以修改，其他用户只读
    """
    
    def has_permission(self, request, view):
        # 允许所有用户进行GET, HEAD, OPTIONS请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 需要登录才能进行其他请求
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # 允许所有用户进行GET, HEAD, OPTIONS请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 作者可以修改自己的内容
        if hasattr(obj, 'user_id') and obj.user_id == request.user.id:
            return True
        
        # 管理员可以修改所有内容
        if request.user.is_superuser:
            return True
        
        # 版主可以修改所属板块的内容
        if hasattr(obj, 'board') and hasattr(request.user, 'role') and request.user.role == 'moderator':
            # 这里需要根据实际情况判断用户是否是该板块的版主
            # 简单实现：假设版主可以管理所有板块
            return True
        
        return False
