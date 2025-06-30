"""
URL configuration for forum_project project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API文档配置
schema_view = get_schema_view(
    openapi.Info(
        title="Forum API",
        default_version='v1',
        description="论坛系统API文档",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),

    # API文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API路由
    path('api/v1/auth/', include('users.urls.auth')),
    path('api/v1/users/', include('users.urls.users')),
    path('api/v1/boards/', include('boards.urls')),
    path('api/v1/posts/', include('posts.urls')),
    path('api/v1/comments/', include('comments.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/reports/', include('reports.urls')),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
