"""
用户认证相关URL配置
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView
)

from users.views_verification import (
    SendVerificationCodeView,
    VerifyEmailView,
    RegisterWithVerificationView,
    ResetPasswordView
)

urlpatterns = [
    # 用户注册 - 旧版本，保留兼容性
    path('register/', RegisterView.as_view(), name='register'),

    # 用户登录
    path('login/', LoginView.as_view(), name='login'),

    # 用户登出
    path('logout/', LogoutView.as_view(), name='logout'),

    # JWT令牌刷新
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 密码重置 - 旧版本，保留兼容性
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # 新版邮箱验证相关接口
    # 发送验证码
    path('verification/send/', SendVerificationCodeView.as_view(), name='send_verification_code'),
    # 验证验证码
    path('verification/verify/', VerifyEmailView.as_view(), name='verify_email'),
    # 带验证码的注册
    path('register/with-verification/', RegisterWithVerificationView.as_view(), name='register_with_verification'),
    # 带验证码的密码重置
    path('password/reset/with-verification/', ResetPasswordView.as_view(), name='reset_password_with_verification'),
]
