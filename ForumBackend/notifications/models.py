"""
消息通知模型
"""

from django.db import models
from django.utils import timezone
from django.conf import settings


class Notification(models.Model):
    """
    消息通知模型
    """
    TYPE_CHOICES = (
        ('comment', '评论通知'),
        ('reply', '回复通知'),
        ('like', '点赞通知'),
        ('system', '系统通知'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收用户'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='sent_notifications',
        null=True,
        blank=True,
        verbose_name='发送用户'
    )
    type = models.CharField('通知类型', max_length=20, choices=TYPE_CHOICES)
    title = models.CharField('通知标题', max_length=100)
    content = models.TextField('通知内容')
    target_type = models.CharField('目标类型', max_length=20, null=True, blank=True)
    target_id = models.PositiveIntegerField('目标ID', null=True, blank=True)
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        verbose_name = '消息通知'
        verbose_name_plural = '消息通知'
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"
