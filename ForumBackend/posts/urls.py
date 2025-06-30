"""
帖子相关URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, LikeViewSet, FavoriteViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'', PostViewSet)

# 创建点赞和收藏路由
like_router = DefaultRouter()
like_router.register(r'likes', LikeViewSet)

favorite_router = DefaultRouter()
favorite_router.register(r'favorites', FavoriteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(like_router.urls)),
    path('', include(favorite_router.urls)),
]
