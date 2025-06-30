"""
板块序列化器
"""

from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import Board

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    """
    用户组序列化器
    """
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserBriefSerializer(serializers.ModelSerializer):
    """
    用户简要信息序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname']


class BoardSerializer(serializers.ModelSerializer):
    """
    板块序列化器
    """
    allowed_groups = GroupSerializer(many=True, read_only=True)
    allowed_users = UserBriefSerializer(many=True, read_only=True)
    access_type_display = serializers.CharField(source='get_access_type_display', read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'name', 'description', 'order',
            'access_type', 'access_type_display', 'allowed_groups', 'allowed_users',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    """
    板块创建和更新序列化器
    """
    allowed_group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    allowed_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Board
        fields = [
            'id', 'name', 'description', 'order',
            'access_type', 'allowed_group_ids', 'allowed_user_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        allowed_group_ids = validated_data.pop('allowed_group_ids', [])
        allowed_user_ids = validated_data.pop('allowed_user_ids', [])

        board = Board.objects.create(**validated_data)

        # 添加允许的用户组
        if allowed_group_ids:
            groups = Group.objects.filter(id__in=allowed_group_ids)
            board.allowed_groups.set(groups)

        # 添加允许的用户
        if allowed_user_ids:
            users = User.objects.filter(id__in=allowed_user_ids)
            board.allowed_users.set(users)

        return board

    def update(self, instance, validated_data):
        allowed_group_ids = validated_data.pop('allowed_group_ids', None)
        allowed_user_ids = validated_data.pop('allowed_user_ids', None)

        # 更新基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新允许的用户组
        if allowed_group_ids is not None:
            groups = Group.objects.filter(id__in=allowed_group_ids)
            instance.allowed_groups.set(groups)

        # 更新允许的用户
        if allowed_user_ids is not None:
            users = User.objects.filter(id__in=allowed_user_ids)
            instance.allowed_users.set(users)

        return instance
