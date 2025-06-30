"""
评论序列化器
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Comment
from users.serializers import UserBriefSerializer

User = get_user_model()


class RecursiveCommentSerializer(serializers.Serializer):
    """
    递归序列化评论回复
    """
    def to_representation(self, instance):
        serializer = CommentSerializer(instance, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    """
    评论序列化器
    """
    user = UserBriefSerializer(read_only=True)
    replies = RecursiveCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'user', 'parent', 'content',
            'likes_count', 'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = [
            'id', 'user', 'likes_count', 'created_at', 'updated_at', 'replies'
        ]


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    创建评论序列化器
    """
    class Meta:
        model = Comment
        fields = ['id', 'post', 'parent', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_parent(self, value):
        """验证父评论是否属于同一帖子"""
        if value and value.post_id != self.initial_data.get('post'):
            raise serializers.ValidationError("父评论必须属于同一帖子")
        return value
    
    def create(self, validated_data):
        # 设置当前用户为评论者
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    更新评论序列化器
    """
    class Meta:
        model = Comment
        fields = ['content']
