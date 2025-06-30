"""
帖子模型
"""

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models import F

from boards.models import Board


class Post(models.Model):
    """
    帖子模型
    """
    title = models.CharField('标题', max_length=255)
    content = models.TextField('内容')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # 用户删除时，删除其发布的所有帖子
        related_name='posts',
        verbose_name='作者'
    )
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,  # 板块删除时，删除该板块下的所有帖子
        related_name='posts',
        verbose_name='所属板块'
    )
    views = models.PositiveIntegerField('浏览量', default=0)
    likes_count = models.PositiveIntegerField('点赞数', default=0)
    comments_count = models.PositiveIntegerField('评论数', default=0)
    is_pinned = models.BooleanField('是否置顶', default=False)
    is_featured = models.BooleanField('是否精华', default=False)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '帖子'
        verbose_name_plural = '帖子'
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),  # 按创建时间降序索引
            models.Index(fields=['user']),  # 按用户索引
            models.Index(fields=['board']),  # 按板块索引
            models.Index(fields=['is_pinned', '-created_at']),  # 置顶和创建时间组合索引
        ]

    def __str__(self):
        return self.title

    def increase_views(self):
        """增加浏览量"""
        self.views += 1
        self.save(update_fields=['views'])

    def update_likes_count(self):
        """更新点赞数"""
        try:
            # 使用正确的查询方式获取点赞数
            likes_count = Like.objects.filter(
                content_type='post',
                content_id=self.id
            ).count()
            
            # 更新点赞数
            self.likes_count = likes_count
            self.save(update_fields=['likes_count'])
            
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"更新帖子点赞数失败，帖子ID: {self.id}, 错误: {str(e)}", exc_info=True)
            return False

    def update_comments_count(self):
        """更新评论数"""
        self.comments_count = self.comments.count()
        self.save(update_fields=['comments_count'])


class Like(models.Model):
    """
    点赞模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # 用户删除时，删除其所有点赞记录
        related_name='likes',
        verbose_name='用户'
    )
    content_type = models.CharField('内容类型', max_length=20, choices=(
        ('post', '帖子'),
        ('comment', '评论'),
    ))
    content_id = models.PositiveIntegerField('内容ID')
    created_at = models.DateTimeField('创建时间', default=timezone.now)

    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        db_table = 'likes'
        ordering = ['-created_at']
        unique_together = ('user', 'content_type', 'content_id') # 确保同一用户不能重复点赞同一内容
        indexes = [
            models.Index(fields=['user']),  # 用户索引
            models.Index(fields=['content_type', 'content_id']),  # 内容索引
        ]

    def __str__(self):
        return f"{self.user.username}点赞了{self.content_type}({self.content_id})"


class Favorite(models.Model):
    """
    收藏模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # 用户删除时，删除其所有收藏记录
        related_name='favorites',
        verbose_name='用户'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,  # 帖子删除时，删除相关的收藏记录
        related_name='favorites',
        verbose_name='帖子'
    )
    created_at = models.DateTimeField('创建时间', default=timezone.now)

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        db_table = 'favorites'
        unique_together = ('user', 'post')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),  # 用户索引
            models.Index(fields=['post']),  # 帖子索引
        ]

    def __str__(self):
        return f"{self.user.username}收藏了{self.post.title}"
