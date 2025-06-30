"""
板块视图
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, F, Q
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from .models import Board
from .serializers import BoardSerializer, BoardCreateUpdateSerializer, GroupSerializer, UserBriefSerializer
from forum_project.utils import success_response, error_response
from forum_project.permissions import IsAdminUserOrReadOnly

User = get_user_model()


class BoardViewSet(viewsets.ModelViewSet):
    """
    板块视图集

    list:
        获取所有板块列表
    retrieve:
        获取单个板块详情
    create:
        创建新板块 (仅管理员)
    update:
        更新板块信息 (仅管理员)
    partial_update:
        部分更新板块信息 (仅管理员)
    destroy:
        删除板块 (仅管理员)
    hot:
        获取热门板块列表
    reorder:
        重新排序板块 (仅管理员)
    groups:
        获取所有用户组 (仅管理员)
    users:
        获取所有用户 (仅管理员)
    """
    queryset = Board.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        """根据不同操作返回不同的序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return BoardCreateUpdateSerializer
        return BoardSerializer

    def get_queryset(self):
        """根据用户权限过滤板块"""
        queryset = super().get_queryset()

        # 管理员可以看到所有板块
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, 'is_admin', False) or getattr(user, 'role', '') == 'admin'):
            return queryset

        # 非管理员只能看到有权限访问的板块
        if not user.is_authenticated:
            # 未登录用户只能看到公开板块
            return queryset.filter(access_type='public')
        else:
            # 已登录用户可以看到公开板块、仅注册用户可见的板块
            query = Q(access_type='public') | Q(access_type='registered')

            # 以及允许其访问的用户特定的板块
            query |= Q(access_type='users', allowed_users=user)

            # 如果用户有groups属性，添加用户组过滤条件
            if hasattr(user, 'groups'):
                try:
                    user_groups = user.groups.all()
                    query |= Q(access_type='groups', allowed_groups__in=user_groups)
                except Exception:
                    # 如果获取用户组失败，忽略用户组过滤条件
                    pass

            return queryset.filter(query).distinct()

    def list(self, request, *args, **kwargs):
        """获取板块列表"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            logger.info("获取板块列表")
            queryset = self.filter_queryset(self.get_queryset())

            # 添加帖子数量统计
            queryset = queryset.annotate(posts_count=Count('posts'))

            serializer = self.get_serializer(queryset, many=True)

            # 添加帖子数量到返回数据
            data = serializer.data
            for i, board in enumerate(queryset):
                data[i]['posts_count'] = board.posts_count

                # 添加当前用户是否有权限访问该板块
                try:
                    board_obj = Board.objects.get(id=board.id)
                    data[i]['can_access'] = board_obj.can_access(request.user)
                except Board.DoesNotExist:
                    data[i]['can_access'] = False
                    logger.warning(f"Board with id {board.id} not found when checking access")

            return success_response(data)
        except Exception as e:
            logger.error(f"Error in board list endpoint: {str(e)}", exc_info=True)
            return error_response(msg=f"获取板块列表失败: {str(e)}", status=500)

    def retrieve(self, request, *args, **kwargs):
        """获取单个板块详情"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            logger.info(f"获取板块详情，ID: {kwargs.get('pk')}")
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            # 添加帖子数量到返回数据
            data = serializer.data
            data['posts_count'] = instance.posts.count()

            # 添加当前用户是否有权限访问该板块
            data['can_access'] = instance.can_access(request.user)

            return success_response(data)
        except Exception as e:
            logger.error(f"获取板块详情失败: {str(e)}", exc_info=True)
            return error_response(msg=f"获取板块详情失败: {str(e)}", status=500)

    def create(self, request, *args, **kwargs):
        """创建新板块 (仅管理员)"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(serializer.data, "板块创建成功")
        return error_response(msg=serializer.errors)

    def update(self, request, *args, **kwargs):
        """更新板块信息 (仅管理员)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response(serializer.data, "板块更新成功")
        return error_response(msg=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """删除板块 (仅管理员)"""
        instance = self.get_object()

        # 检查板块下是否有帖子
        if instance.posts.exists():
            return error_response(msg="该板块下存在帖子，无法删除", status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return success_response(msg="板块删除成功")

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def hot(self, request):
        """获取热门板块列表"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            # 获取请求参数
            limit = request.query_params.get('limit', 5)
            try:
                limit = int(limit)
            except ValueError:
                limit = 5
                logger.warning(f"Invalid limit parameter: {request.query_params.get('limit')}, using default: 5")

            logger.info(f"Getting hot boards with limit: {limit}")

            # 按帖子数量排序获取热门板块，但只包括用户有权限访问的板块
            queryset = self.get_queryset().annotate(posts_count=Count('posts')).order_by('-posts_count')[:limit]

            logger.info(f"Found {queryset.count()} hot boards")

            serializer = self.get_serializer(queryset, many=True)

            # 添加帖子数量到返回数据
            data = serializer.data
            for i, board in enumerate(queryset):
                data[i]['posts_count'] = board.posts_count

                # 添加当前用户是否有权限访问该板块
                try:
                    board_obj = Board.objects.get(id=board.id)
                    data[i]['can_access'] = board_obj.can_access(request.user)
                except Board.DoesNotExist:
                    data[i]['can_access'] = False
                    logger.warning(f"Board with id {board.id} not found when checking access")

            return success_response(data)
        except Exception as e:
            logger.error(f"Error in hot boards endpoint: {str(e)}", exc_info=True)
            return error_response(msg=f"获取热门板块失败: {str(e)}", status=500)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reorder(self, request):
        """重新排序板块 (仅管理员)"""
        board_orders = request.data.get('board_orders', [])

        if not isinstance(board_orders, list):
            return error_response(msg="board_orders必须是一个列表", status=status.HTTP_400_BAD_REQUEST)

        # 批量更新板块顺序
        for item in board_orders:
            if not isinstance(item, dict) or 'id' not in item or 'order' not in item:
                continue

            try:
                board_id = int(item['id'])
                order = int(item['order'])
                Board.objects.filter(id=board_id).update(order=order)
            except (ValueError, Board.DoesNotExist):
                continue

        return success_response(msg="板块排序更新成功")

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def groups(self, request):
        """获取所有用户组 (仅管理员)"""
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return success_response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def users(self, request):
        """获取所有用户 (仅管理员)"""
        users = User.objects.all()
        serializer = UserBriefSerializer(users, many=True)
        return success_response(serializer.data)
