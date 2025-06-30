"""
消息通知视图
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Notification
from .serializers import NotificationSerializer
from forum_project.utils import success_response, error_response


class NotificationViewSet(viewsets.ModelViewSet):
    """
    消息通知视图集
    
    list:
        获取当前用户的消息通知列表
    retrieve:
        获取消息通知详情
    read:
        将消息标记为已读
    read_all:
        将所有消息标记为已读
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'is_read']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """只返回当前用户的消息通知"""
        return Notification.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """获取当前用户的消息通知列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """获取消息通知详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)
    
    @action(detail=True, methods=['put'])
    def read(self, request, pk=None):
        """将消息标记为已读"""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return success_response(msg="消息已标记为已读")
    
    @action(detail=False, methods=['put'])
    def read_all(self, request):
        """将所有消息标记为已读"""
        queryset = self.get_queryset().filter(is_read=False)
        queryset.update(is_read=True)
        return success_response(msg="所有消息已标记为已读")
    
    def create(self, request, *args, **kwargs):
        """禁止通过API创建消息"""
        return error_response(msg="不允许通过此API创建消息", status=status.HTTP_403_FORBIDDEN)
    
    def update(self, request, *args, **kwargs):
        """禁止通过API更新消息"""
        return error_response(msg="不允许通过此API更新消息", status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        """删除消息"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(msg="消息已删除")
