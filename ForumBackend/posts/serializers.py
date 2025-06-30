"""
帖子序列化器
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Post, Like, Favorite
from boards.serializers import BoardSerializer
from users.serializers import UserBriefSerializer

User = get_user_model()


class PostListSerializer(serializers.ModelSerializer):
    """
    帖子列表序列化器
    """
    user = UserBriefSerializer(read_only=True)
    board_name = serializers.CharField(source='board.name', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'user', 'board_name', 'views',
            'likes_count', 'comments_count', 'is_pinned',
            'is_featured', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'views', 'likes_count', 'comments_count',
            'is_pinned', 'is_featured', 'created_at', 'updated_at'
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """
    帖子详情序列化器
    """
    user = UserBriefSerializer(read_only=True)
    board = BoardSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'user', 'board',
            'views', 'likes_count', 'comments_count',
            'is_pinned', 'is_featured', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'views', 'likes_count', 'comments_count',
            'is_pinned', 'is_featured', 'created_at', 'updated_at'
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    """
    创建帖子序列化器
    """
    class Meta:
        model = Post
        fields = ['title', 'content', 'board']

    def create(self, validated_data):
        # 设置当前用户为作者
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PostUpdateSerializer(serializers.ModelSerializer):
    """
    更新帖子序列化器
    """
    class Meta:
        model = Post
        fields = ['title', 'content', 'board']


class LikeSerializer(serializers.ModelSerializer):
    """
    点赞序列化器
    """
    user = UserBriefSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'content_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class LikeCreateSerializer(serializers.ModelSerializer):
    """
    创建点赞序列化器
    """
    class Meta:
        model = Like
        fields = ['content_type', 'content_id']

    def validate(self, attrs):
        # 验证内容类型和内容ID是否存在
        content_type = attrs.get('content_type')
        content_id = attrs.get('content_id')

        if content_type == 'post':
            try:
                Post.objects.get(id=content_id)
            except Post.DoesNotExist:
                raise serializers.ValidationError({
                    'content_id': f'帖子ID {content_id} 不存在'
                })
        elif content_type == 'comment':
            from comments.models import Comment
            try:
                Comment.objects.get(id=content_id)
            except Comment.DoesNotExist:
                raise serializers.ValidationError({
                    'content_id': f'评论ID {content_id} 不存在'
                })

        # 检查是否已经点赞
        user = self.context['request'].user
        if Like.objects.filter(user=user, content_type=content_type, content_id=content_id).exists():
            raise serializers.ValidationError('您已经点赞过该内容')

        return attrs

    def create(self, validated_data):
        # 设置当前用户
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """
    收藏序列化器
    """
    user = UserBriefSerializer(read_only=True)
    post = PostListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """
    创建收藏序列化器
    """
    class Meta:
        model = Favorite
        fields = ['post']

    def validate_post(self, value):
        # 检查是否已经收藏
        user = self.context['request'].user
        if Favorite.objects.filter(user=user, post=value).exists():
            raise serializers.ValidationError('您已经收藏过该帖子')
        return value

    def create(self, validated_data):
        # 设置当前用户
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
