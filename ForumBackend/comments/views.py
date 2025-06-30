"""
评论视图
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Comment
from .serializers import (
    CommentSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer
)
from forum_project.utils import success_response, error_response
from forum_project.permissions import IsAuthorOrModeratorOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    """
    评论视图集

    list:
        获取评论列表
    retrieve:
        获取评论详情
    create:
        创建评论
    update:
        更新评论
    partial_update:
        部分更新评论
    destroy:
        删除评论
    """
    queryset = Comment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'user', 'parent']
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['created_at']

    def get_serializer_class(self):
        """根据不同操作返回不同的序列化器"""
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CommentUpdateSerializer
        return CommentSerializer

    def get_permissions(self):
        """根据不同操作设置不同的权限"""
        if self.action in ['create']:
            # 创建评论需要登录
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 更新和删除评论需要是作者或版主
            return [IsAuthorOrModeratorOrReadOnly()]
        # 其他操作允许所有人
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        """获取评论列表"""
        # 只获取顶级评论（没有父评论的评论）
        queryset = self.filter_queryset(self.get_queryset())
        if 'parent' not in request.query_params:
            queryset = queryset.filter(parent=None)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """获取评论详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

    def create(self, request, *args, **kwargs):
        """创建评论"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            comment = self.perform_create(serializer)
            
            # 使用CommentSerializer返回完整的评论信息
            response_serializer = CommentSerializer(comment)
            
            # 更新帖子的评论数
            post = comment.post
            post.update_comments_count()
            
            return success_response(response_serializer.data, "评论发表成功")
        return error_response(msg=serializer.errors)

    def perform_create(self, serializer):
        """执行创建评论"""
        return serializer.save()

    def update(self, request, *args, **kwargs):
        """更新评论"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response(serializer.data, "评论更新成功")
        return error_response(msg=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """删除评论"""
        instance = self.get_object()

        # 获取评论ID和帖子ID，用于记录日志
        comment_id = instance.id
        post = instance.post
        post_id = post.id if post else None

        # 检查是否有子评论（回复）
        has_replies = instance.replies.exists()

        # 如果有子评论，可以选择一起删除或者将子评论变为顶级评论
        # 这里选择一起删除子评论
        if has_replies:
            # 记录子评论数量
            replies_count = instance.replies.count()
            print(f"删除评论 ID={comment_id} 及其 {replies_count} 条回复")

        # 删除评论（Django会自动级联删除与评论相关的点赞，因为它们使用了CASCADE关联）
        self.perform_destroy(instance)

        # 更新帖子评论数
        if post:
            post.update_comments_count()

        # 记录日志
        print(f"评论已删除: ID={comment_id}, 帖子ID={post_id}, 用户={request.user.username}")

        return success_response(msg="评论删除成功")
