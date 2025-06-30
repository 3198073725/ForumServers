from .models import Notification

def create_notification(user, notification_type, content, related_object=None):
    """
    创建通知
    
    Args:
        user: 接收通知的用户
        notification_type: 通知类型，如'like', 'comment', 'follow', 'system'
        content: 通知内容
        related_object: 相关对象，如帖子、评论等
    
    Returns:
        Notification: 创建的通知对象
    """
    try:
        # 创建通知记录
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            content=content,
            related_object=related_object
        )
        return notification
    except Exception as e:
        print(f"创建通知失败: {e}")
        return None

def get_unread_notification_count(user):
    """
    获取用户未读通知数量
    
    Args:
        user: 用户对象
    Returns:
        int: 未读通知数量
    """
    try:
        # 获取未读通知数量
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
        return unread_count
    except Exception as e:
        print(f"获取未读通知数量失败: {e}")
        return 0