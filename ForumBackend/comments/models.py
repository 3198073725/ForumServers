"""
评论模型
"""

from django.db import models
from django.utils import timezone
from django.conf import settings

from posts.models import Post


class Comment(models.Model):
    """
    评论模型
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,  # 帖子删除时，删除该帖子下的所有评论
        related_name='comments',
        verbose_name='所属帖子'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # 用户删除时，删除其发布的所有评论
        related_name='comments',
        verbose_name='评论用户'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,  # 父评论删除时，子评论保留，但parent设为NULL
        related_name='replies',
        null=True,
        blank=True,
        verbose_name='父评论'
    )
    content = models.TextField('评论内容')
    likes_count = models.PositiveIntegerField('点赞数', default=0)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post']),  # 按帖子索引，加速查询特定帖子的评论
            models.Index(fields=['user']),  # 按用户索引，加速查询用户的评论
            models.Index(fields=['parent']),  # 按父评论索引，加速查询回复
            models.Index(fields=['created_at']),  # 按创建时间索引，加速排序
        ]
    
    def __str__(self):
        return f"{self.user.username}的评论"
    
    def save(self, *args, **kwargs):
        """重写保存方法，更新帖子评论数"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # 如果是新评论，更新帖子评论数
        if is_new and self.post:
            self.post.update_comments_count()
    
    def delete(self, *args, **kwargs):
        """重写删除方法，更新帖子评论数"""
        post = self.post
        super().delete(*args, **kwargs)
        
        # 更新帖子评论数
        if post:
            post.update_comments_count()
    
    def update_likes_count(self):
        """更新点赞数"""
        from posts.models import Like
        # 使用更高效的查询直接获取点赞数
        self.likes_count = Like.objects.filter(content_type='comment', content_id=self.id).count()
        self.save(update_fields=['likes_count'])
