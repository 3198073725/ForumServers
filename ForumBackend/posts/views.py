"""
帖子视图
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import Prefetch, Count
import os
import uuid
import logging
import traceback

from .models import Post, Like, Favorite
from comments.models import Comment  # 添加评论模型导入
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
    LikeSerializer,
    LikeCreateSerializer,
    FavoriteSerializer,
    FavoriteCreateSerializer
)
from forum_project.utils import success_response, error_response, cached_view, invalidate_cache_pattern
from forum_project.permissions import IsAuthorOrModeratorOrReadOnly

# 获取logger
logger = logging.getLogger(__name__)

class PostViewSet(viewsets.ModelViewSet):
    """
    帖子视图集

    list:
        获取帖子列表
    retrieve:
        获取帖子详情
    create:
        创建帖子
    update:
        更新帖子
    partial_update:
        部分更新帖子
    destroy:
        删除帖子
    pin:
        置顶/取消置顶帖子
    feature:
        加精/取消加精帖子
    """
    queryset = Post.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['board', 'user', 'is_pinned', 'is_featured']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views', 'likes_count', 'comments_count']
    ordering = ['-is_pinned', '-created_at']

    def get_serializer_class(self):
        """根据不同操作返回不同的序列化器"""
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        elif self.action == 'create':
            return PostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PostUpdateSerializer
        return PostDetailSerializer

    def get_permissions(self):
        """根据不同操作设置不同的权限"""
        if self.action in ['create']:
            # 创建帖子需要登录
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 更新和删除帖子需要是作者或版主
            return [IsAuthorOrModeratorOrReadOnly()]
        elif self.action in ['pin', 'feature']:
            # 置顶和加精需要是版主或管理员
            return [permissions.IsAdminUser()]
        # 其他操作允许所有人
        return [permissions.AllowAny()]

    def get_queryset(self):
        """
        根据不同操作返回优化的查询集
        """
        queryset = super().get_queryset()

        if self.action == 'list':
            # 列表页面优化查询，预加载用户和板块信息
            queryset = queryset.select_related('user', 'board')
        elif self.action == 'retrieve':
            # 详情页面优化查询，预加载用户、板块和评论信息
            queryset = queryset.select_related('user', 'board')
            # 预加载评论及其用户信息
            queryset = queryset.prefetch_related(
                Prefetch(
                    'comments',
                    queryset=Comment.objects.all().select_related('user').filter(parent=None)
                )
            )

        return queryset

    @cached_view('home_posts')
    def list(self, request, *args, **kwargs):
        """获取帖子列表"""
        try:
            logger.info(f"获取帖子列表，参数: {request.query_params}")

            # 获取查询参数
            board_id = request.query_params.get('board')
            if board_id:
                logger.info(f"按板块筛选，板块ID: {board_id}")
                # 如果是按板块筛选，使用board_posts缓存键
                self._cache_key_prefix = 'board_posts'

            queryset = self.filter_queryset(self.get_queryset())
            logger.info(f"筛选后的帖子数量: {queryset.count()}")

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return success_response(serializer.data)
        except DatabaseError as e:
            # 只捕获数据库相关异常
            logger.error(f"获取帖子列表时数据库错误: {str(e)}", exc_info=True)
            return error_response(msg=f"数据库查询错误: {str(e)}", status=500)
        except Exception as e:
            # 记录未预期的异常，但不捕获，让它正常抛出
            logger.error(f"获取帖子列表时未预期的错误: {str(e)}", exc_info=True)
            raise

    # 暂时禁用缓存装饰器
    # @cached_view('post_detail')
    def retrieve(self, request, *args, **kwargs):
        """获取帖子详情"""
        try:
            logger.info(f"获取帖子详情，ID: {kwargs.get('pk')}")
            instance = self.get_object()
            logger.info(f"成功获取帖子对象，标题: {instance.title}")
            
            # 增加浏览量
            try:
                instance.increase_views()
                logger.info(f"增加浏览量成功，当前浏览量: {instance.views}")
            except Exception as e:
                logger.error(f"增加浏览量失败: {str(e)}", exc_info=True)
                # 继续处理，不要因为浏览量更新失败而中断整个请求
            
            serializer = self.get_serializer(instance)
            logger.info(f"帖子序列化成功，准备返回数据")
            return success_response(serializer.data)
        except DatabaseError as e:
            logger.error(f"获取帖子详情时数据库错误: {str(e)}", exc_info=True)
            return error_response(msg=f"数据库查询错误: {str(e)}", status=500)
        except Exception as e:
            # 捕获所有异常，确保返回友好的错误信息
            logger.error(f"获取帖子详情时发生未知错误: {str(e)}")
            logger.error(traceback.format_exc())
            return error_response(msg=f"服务器内部错误: {str(e)}", status=500)

    def create(self, request, *args, **kwargs):
        """创建帖子"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                # 清除相关缓存
                invalidate_cache_pattern('home_posts:*')
                board_id = serializer.validated_data.get('board').id
                invalidate_cache_pattern(f'board_posts:*/api/v1/posts/?board={board_id}*')
                return success_response(serializer.data, "帖子发布成功")
            except IntegrityError as e:
                logger.error(f"创建帖子时完整性错误: {str(e)}", exc_info=True)
                return error_response(msg="数据完整性错误，请检查输入", status=400)
            except DatabaseError as e:
                logger.error(f"创建帖子时数据库错误: {str(e)}", exc_info=True)
                return error_response(msg=f"数据库错误: {str(e)}", status=500)
        return error_response(msg=serializer.errors)

    def update(self, request, *args, **kwargs):
        """更新帖子"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            try:
                self.perform_update(serializer)
                # 清除相关缓存
                invalidate_cache_pattern(f'post_detail:*/api/v1/posts/{instance.id}/*')
                invalidate_cache_pattern('home_posts:*')
                board_id = instance.board.id
                invalidate_cache_pattern(f'board_posts:*/api/v1/posts/?board={board_id}*')
                return success_response(serializer.data, "帖子更新成功")
            except DatabaseError as e:
                logger.error(f"更新帖子时数据库错误: {str(e)}", exc_info=True)
                return error_response(msg=f"数据库错误: {str(e)}", status=500)
        return error_response(msg=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """删除帖子"""
        try:
            instance = self.get_object()

            # 获取帖子ID，用于记录日志
            post_id = instance.id
            post_title = instance.title
            board_id = instance.board.id

            # 删除帖子（Django会自动级联删除与帖子相关的评论、点赞和收藏，因为它们使用了CASCADE关联）
            self.perform_destroy(instance)

            # 清除相关缓存
            invalidate_cache_pattern(f'post_detail:*/api/v1/posts/{post_id}/*')
            invalidate_cache_pattern('home_posts:*')
            invalidate_cache_pattern(f'board_posts:*/api/v1/posts/?board={board_id}*')

            # 记录日志
            logger.info(f"帖子已删除: ID={post_id}, 标题={post_title}, 用户={request.user.username}")

            return success_response(msg="帖子删除成功")
        except DatabaseError as e:
            logger.error(f"删除帖子时数据库错误: {str(e)}", exc_info=True)
            return error_response(msg=f"数据库错误: {str(e)}", status=500)

    @action(detail=True, methods=['put'])
    def pin(self, request, pk=None):
        """置顶/取消置顶帖子"""
        try:
            post = self.get_object()
            post.is_pinned = not post.is_pinned
            post.save()
            
            # 清除相关缓存
            invalidate_cache_pattern(f'post_detail:*/api/v1/posts/{post.id}/*')
            invalidate_cache_pattern('home_posts:*')
            board_id = post.board.id
            invalidate_cache_pattern(f'board_posts:*/api/v1/posts/?board={board_id}*')
            
            action = "置顶" if post.is_pinned else "取消置顶"
            return success_response(msg=f"帖子{action}成功")
        except DatabaseError as e:
            logger.error(f"置顶/取消置顶帖子时数据库错误: {str(e)}", exc_info=True)
            return error_response(msg=f"数据库错误: {str(e)}", status=500)

    @action(detail=True, methods=['put'])
    def feature(self, request, pk=None):
        """加精/取消加精帖子"""
        try:
            post = self.get_object()
            post.is_featured = not post.is_featured
            post.save()
            
            # 清除相关缓存
            invalidate_cache_pattern(f'post_detail:*/api/v1/posts/{post.id}/*')
            invalidate_cache_pattern('home_posts:*')
            board_id = post.board.id
            invalidate_cache_pattern(f'board_posts:*/api/v1/posts/?board={board_id}*')
            
            action = "加精" if post.is_featured else "取消加精"
            return success_response(msg=f"帖子{action}成功")
        except DatabaseError as e:
            logger.error(f"加精/取消加精帖子时数据库错误: {str(e)}", exc_info=True)
            return error_response(msg=f"数据库错误: {str(e)}", status=500)

    @action(detail=True, methods=['get'])
    def like_status(self, request, pk=None):
        """获取点赞状态"""
        try:
            # 未登录用户默认未点赞
            if not request.user.is_authenticated:
                return success_response({'is_liked': False})

            # 获取帖子
            try:
                post = self.get_object()
            except Exception as e:
                logger.error(f"获取帖子失败，ID: {pk}, 错误: {str(e)}")
                return error_response(msg="帖子不存在或已被删除", status=404)

            # 检查是否已点赞
            is_liked = Like.objects.filter(
                user=request.user,
                content_type='post',
                content_id=post.id
            ).exists()
            
            return success_response({'is_liked': is_liked})
        except Exception as e:
            logger.error(f"获取点赞状态失败: {str(e)}", exc_info=True)
            return error_response(msg="获取点赞状态失败", status=500)

    @action(detail=True, methods=['get'])
    def favorite_status(self, request, pk=None):
        """获取收藏状态"""
        try:
            # 未登录用户默认未收藏
            if not request.user.is_authenticated:
                return success_response({'is_favorited': False})

            # 获取帖子
            try:
                post = self.get_object()
            except Exception as e:
                logger.error(f"获取帖子失败，ID: {pk}, 错误: {str(e)}")
                return error_response(msg="帖子不存在或已被删除", status=404)

            # 检查是否已收藏
            is_favorited = Favorite.objects.filter(
                user=request.user,
                post=post
            ).exists()
            
            return success_response({'is_favorited': is_favorited})
        except Exception as e:
            logger.error(f"获取收藏状态失败: {str(e)}", exc_info=True)
            return error_response(msg="获取收藏状态失败", status=500)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞帖子"""
        try:
            # 检查用户是否登录
            if not request.user.is_authenticated:
                return error_response(msg="请先登录", status=401)

            # 获取帖子
            try:
                post = self.get_object()
            except Exception as e:
                logger.error(f"获取帖子失败，ID: {pk}, 错误: {str(e)}")
                return error_response(msg="帖子不存在或已被删除", status=404)

            user = request.user
            logger.info(f"用户 {user.username} 尝试点赞/取消点赞帖子 {post.id}")

            # 使用select_for_update确保数据一致性
            with transaction.atomic():
                # 检查是否已经点赞
                like = Like.objects.filter(
                    user=user,
                    content_type='post',
                    content_id=post.id
                ).select_for_update().first()

                if like:
                    # 如果已经点赞，则取消点赞
                    try:
                        like.delete()
                        # 更新帖子点赞数
                        if not post.update_likes_count():
                            logger.error(f"取消点赞后更新点赞数失败，帖子ID: {post.id}")
                            return error_response(msg="取消点赞失败，请稍后重试", status=500)
                        logger.info(f"用户 {user.username} 成功取消点赞帖子 {post.id}")
                        return success_response(msg="取消点赞成功")
                    except Exception as e:
                        logger.error(f"取消点赞失败: {str(e)}", exc_info=True)
                        return error_response(msg="取消点赞失败，请稍后重试", status=500)

                # 创建新的点赞
                try:
                    Like.objects.create(
                        user=user,
                        content_type='post',
                        content_id=post.id
                    )
                    # 更新帖子点赞数
                    if not post.update_likes_count():
                        logger.error(f"点赞后更新点赞数失败，帖子ID: {post.id}")
                        return error_response(msg="点赞失败，请稍后重试", status=500)
                    logger.info(f"用户 {user.username} 成功点赞帖子 {post.id}")
                    return success_response(msg="点赞成功")
                except IntegrityError:
                    logger.warning(f"用户 {user.username} 重复点赞帖子 {post.id}")
                    return error_response(msg="您已经点赞过该帖子", status=400)
                except Exception as e:
                    logger.error(f"点赞失败: {str(e)}", exc_info=True)
                    return error_response(msg="点赞失败，请稍后重试", status=500)

        except Exception as e:
            logger.error(f"点赞操作异常: {str(e)}", exc_info=True)
            return error_response(msg="操作失败，请稍后重试", status=500)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """收藏帖子"""
        try:
            # 检查用户是否登录
            if not request.user.is_authenticated:
                return error_response(msg="请先登录", status=401)
                
            # 获取帖子
            try:
                post = self.get_object()
            except Exception as e:
                logger.error(f"获取帖子失败，ID: {pk}, 错误: {str(e)}")
                return error_response(msg="帖子不存在或已被删除", status=404)

            user = request.user
            logger.info(f"用户 {user.username} 尝试收藏/取消收藏帖子 {post.id}")

            # 如果已经收藏，则取消收藏
            favorite = Favorite.objects.filter(user=user, post=post).first()
            if favorite:
                favorite.delete()
                
                # 清除相关缓存
                invalidate_cache_pattern(f'post_detail:*/api/v1/posts/{post.id}/*')
                
                logger.info(f"用户 {user.username} 成功取消收藏帖子 {post.id}")
                return success_response(data={"is_favorited": False}, msg="取消收藏成功")

            # 创建收藏
            try:
                Favorite.objects.create(user=user, post=post)
                
                # 清除相关缓存
                invalidate_cache_pattern(f'post_detail:*/api/v1/posts/{post.id}/*')
                
                logger.info(f"用户 {user.username} 成功收藏帖子 {post.id}")
                return success_response(data={"is_favorited": True}, msg="收藏成功")
            except IntegrityError:
                logger.warning(f"用户 {user.username} 重复收藏帖子 {post.id}")
                return error_response(msg="您已经收藏过该帖子", status=400)
            except Exception as e:
                logger.error(f"收藏失败: {str(e)}", exc_info=True)
                return error_response(msg="收藏失败，请稍后重试", status=500)
                
        except DatabaseError as e:
            logger.error(f"收藏/取消收藏帖子时数据库错误: {str(e)}", exc_info=True)
            return error_response(msg=f"数据库错误: {str(e)}", status=500)
        except Exception as e:
            logger.error(f"收藏操作异常: {str(e)}", exc_info=True)
            return error_response(msg="操作失败，请稍后重试", status=500)

    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        """上传帖子图片"""
        if not request.FILES.get('image'):
            return error_response(msg="请选择要上传的图片")

        image = request.FILES['image']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if image.content_type not in allowed_types:
            return error_response(msg="只支持JPG、PNG和GIF格式的图片")

        # 验证文件大小（限制为5MB）
        if image.size > 5 * 1024 * 1024:
            return error_response(msg="图片大小不能超过5MB")

        try:
            # 生成唯一的文件名
            ext = os.path.splitext(image.name)[1]
            filename = f"post_images/{uuid.uuid4()}{ext}"
            
            # 保存文件
            path = default_storage.save(filename, ContentFile(image.read()))
            
            # 获取文件的URL
            url = default_storage.url(path)
            
            return success_response({"url": url}, "图片上传成功")
        except Exception as e:
            logger.error(f"上传图片时发生错误: {str(e)}", exc_info=True)
            return error_response(msg=f"图片上传失败: {str(e)}", status=500)


class LikeViewSet(viewsets.ModelViewSet):
    """
    点赞视图集

    list:
        获取点赞列表
    retrieve:
        获取点赞详情
    create:
        创建点赞
    destroy:
        删除点赞
    """
    queryset = Like.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'content_type', 'content_id']

    def get_serializer_class(self):
        """根据不同操作返回不同的序列化器"""
        if self.action == 'create':
            return LikeCreateSerializer
        return LikeSerializer

    def get_permissions(self):
        """根据不同操作设置不同的权限"""
        if self.action in ['create', 'destroy']:
            # 创建和删除点赞需要登录
            return [permissions.IsAuthenticated()]
        # 其他操作允许所有人
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        """获取点赞列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """获取点赞详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

    def create(self, request, *args, **kwargs):
        """创建点赞"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 检查是否已经点赞
            content_type = serializer.validated_data['content_type']
            content_id = serializer.validated_data['content_id']
            user = request.user

            # 如果已经点赞，则返回错误
            if Like.objects.filter(user=user, content_type=content_type, content_id=content_id).exists():
                return error_response(msg="您已经点赞过该内容")

            like = serializer.save(user=user)

            # 更新内容的点赞数
            if content_type == 'post':
                try:
                    post = Post.objects.get(id=content_id)
                    post.update_likes_count()
                except Post.DoesNotExist:
                    pass
            elif content_type == 'comment':
                from comments.models import Comment
                try:
                    comment = Comment.objects.get(id=content_id)
                    comment.update_likes_count()
                except Comment.DoesNotExist:
                    pass

            return success_response(self.get_serializer(like).data, "点赞成功")
        return error_response(msg=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """删除点赞"""
        instance = self.get_object()

        # 只能删除自己的点赞
        if instance.user != request.user:
            return error_response(msg="您无权删除该点赞", status=status.HTTP_403_FORBIDDEN)

        content_type = instance.content_type
        content_id = instance.content_id

        self.perform_destroy(instance)

        # 更新内容的点赞数
        if content_type == 'post':
            try:
                post = Post.objects.get(id=content_id)
                post.update_likes_count()
            except Post.DoesNotExist:
                pass
        elif content_type == 'comment':
            from comments.models import Comment
            try:
                comment = Comment.objects.get(id=content_id)
                comment.update_likes_count()
            except Comment.DoesNotExist:
                pass

        return success_response(msg="取消点赞成功")


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    收藏视图集

    list:
        获取收藏列表
    retrieve:
        获取收藏详情
    create:
        创建收藏
    destroy:
        删除收藏
    """
    queryset = Favorite.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'post']

    def get_serializer_class(self):
        """根据不同操作返回不同的序列化器"""
        if self.action == 'create':
            return FavoriteCreateSerializer
        return FavoriteSerializer

    def get_permissions(self):
        """根据不同操作设置不同的权限"""
        if self.action in ['create', 'destroy']:
            # 创建和删除收藏需要登录
            return [permissions.IsAuthenticated()]
        # 其他操作允许所有人
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        """获取收藏列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """获取收藏详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

    def create(self, request, *args, **kwargs):
        """创建收藏"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 检查是否已经收藏
            post = serializer.validated_data['post']
            user = request.user

            # 如果已经收藏，则返回错误
            if Favorite.objects.filter(user=user, post=post).exists():
                return error_response(msg="您已经收藏过该帖子")

            favorite = serializer.save(user=user)
            return success_response(self.get_serializer(favorite).data, "收藏成功")
        return error_response(msg=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """删除收藏"""
        instance = self.get_object()

        # 只能删除自己的收藏
        if instance.user != request.user:
            return error_response(msg="您无权删除该收藏", status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return success_response(msg="取消收藏成功")