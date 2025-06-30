"""
用户信息重定向URL配置
"""

from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    # 重定向 /users/profile/me/ 到 /api/v1/users/profile/me/
    path('profile/me/', RedirectView.as_view(url='/api/v1/users/profile/me/', permanent=False), name='profile_redirect'),
    
    # 重定向 /users/profile/me/posts/ 到 /api/v1/users/profile/me/posts/
    path('profile/me/posts/', RedirectView.as_view(url='/api/v1/users/profile/me/posts/', permanent=False), name='profile_posts_redirect'),
    
    # 重定向 /users/profile/me/comments/ 到 /api/v1/users/profile/me/comments/
    path('profile/me/comments/', RedirectView.as_view(url='/api/v1/users/profile/me/comments/', permanent=False), name='profile_comments_redirect'),
    
    # 重定向 /users/profile/me/favorites/ 到 /api/v1/users/profile/me/favorites/
    path('profile/me/favorites/', RedirectView.as_view(url='/api/v1/users/profile/me/favorites/', permanent=False), name='profile_favorites_redirect'),
]
