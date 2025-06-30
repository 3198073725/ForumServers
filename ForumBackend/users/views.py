"""
用户相关视图
"""

from rest_framework import status, permissions, viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.contrib.auth import logout
from django.db.models import Count

from .models import User
from posts.models import Post, Favorite
from comments.models import Comment
from posts.serializers import PostListSerializer, FavoriteSerializer
from comments.serializers import CommentSerializer
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from forum_project.utils import success_response, error_response


class RegisterView(APIView):
    """
    用户注册视图
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return success_response(msg="注册成功")
        return error_response(msg=serializer.errors)


class LoginView(APIView):
    """
    用户登录视图
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # 更新最后登录时间
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)

            # 返回用户信息和令牌
            user_data = UserDetailSerializer(user).data

            return success_response({
                'token': token,
                'user_info': user_data
            }, "登录成功")

        return error_response(msg="用户名或密码错误", status=401)


class LogoutView(APIView):
    """
    用户登出视图
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 前端应该清除本地存储的token
        # 后端可以记录登出日志或进行其他操作
        return success_response(msg="登出成功")


class UserProfileView(APIView):
    """
    用户个人信息视图
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取当前用户信息"""
        serializer = UserDetailSerializer(request.user)
        return success_response(serializer.data)

    def put(self, request):
        """更新当前用户信息"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(UserDetailSerializer(request.user).data, "个人信息更新成功")
        return error_response(msg=serializer.errors)


class PasswordChangeView(APIView):
    """
    密码修改视图
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            # 更新密码后，用户需要重新登录
            return success_response(msg="密码修改成功，请重新登录")

        return error_response(msg=serializer.errors)


class PasswordResetRequestView(APIView):
    """
    密码重置请求视图
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            # 在实际项目中，这里应该生成重置令牌并发送邮件
            # 为了演示，我们简单返回成功消息
            return success_response(msg="密码重置链接已发送到您的邮箱")

        return error_response(msg=serializer.errors)


class PasswordResetConfirmView(APIView):
    """
    密码重置确认视图
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            # 在实际项目中，这里应该验证令牌并重置密码
            # 为了演示，我们简单返回成功消息
            return success_response(msg="密码重置成功，请使用新密码登录")

        return error_response(msg=serializer.errors)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    用户个人中心视图集

    retrieve:
        获取用户信息
    update:
        更新用户信息
    posts:
        获取用户发布的帖子
    comments:
        获取用户的评论
    favorites:
        获取用户收藏的帖子
    hot:
        获取热门用户列表
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """根据不同操作设置不同的权限"""
        if self.action == 'hot':
            return [AllowAny()]
        elif self.action in ['retrieve']:
            # 查看用户信息允许所有人
            return [AllowAny()]
        # 其他操作需要登录
        return [IsAuthenticated()]

    def get_object(self):
        """获取当前用户或指定用户"""
        if self.kwargs.get('pk') == 'me':
            # 如果请求的是 /users/me/，返回当前登录用户
            return self.request.user
        # 否则按正常方式获取用户
        return super().get_object()

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """获取用户发布的帖子"""
        user = self.get_object()
        posts = Post.objects.filter(user=user).order_by('-created_at')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PostListSerializer(posts, many=True)
        return success_response(serializer.data)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取用户的评论"""
        user = self.get_object()
        comments = Comment.objects.filter(user=user).order_by('-created_at')
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(comments, many=True)
        return success_response(serializer.data)

    @action(detail=True, methods=['get'])
    def favorites(self, request, pk=None):
        """获取用户收藏的帖子"""
        user = self.get_object()
        favorites = Favorite.objects.filter(user=user).order_by('-created_at')
        page = self.paginate_queryset(favorites)
        if page is not None:
            serializer = FavoriteSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FavoriteSerializer(favorites, many=True)
        return success_response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def hot(self, request):
        """获取热门用户列表"""
        # 获取请求参数
        limit = request.query_params.get('limit', 5)
        try:
            limit = int(limit)
        except ValueError:
            limit = 5

        # 按帖子数量排序获取热门用户
        queryset = User.objects.annotate(posts_count=Count('posts')).order_by('-posts_count')[:limit]

        serializer = self.get_serializer(queryset, many=True)

        # 添加帖子数量到返回数据
        data = serializer.data
        for i, user in enumerate(queryset):
            data[i]['posts_count'] = user.posts_count

        return success_response(data)
