"""
消息通知序列化器
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Notification
from users.serializers import UserBriefSerializer

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """
    消息通知序列化器
    """
    sender = UserBriefSerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'sender', 'type', 'type_display', 'title', 'content',
            'target_type', 'target_id', 'is_read', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'sender', 'type', 'type_display', 'title', 'content',
            'target_type', 'target_id', 'created_at'
        ]
