"""
验证码相关视图
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .serializers_verification import (
    SendVerificationCodeSerializer,
    VerifyEmailSerializer,
    RegisterWithVerificationSerializer,
    ResetPasswordSerializer
)
from .utils import send_verification_email
from forum_project.utils import success_response, error_response


class SendVerificationCodeView(APIView):
    """
    发送验证码视图
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SendVerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code_type = serializer.validated_data['type']
            
            # 发送验证码邮件
            success, result = send_verification_email(email, code_type)
            
            if success:
                return success_response(msg="验证码已发送，请查收邮件")
            else:
                return error_response(msg=f"发送验证码失败: {result}")
        
        return error_response(msg=serializer.errors)


class VerifyEmailView(APIView):
    """
    验证邮箱视图
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            return success_response(msg="验证码验证成功")
        
        return error_response(msg=serializer.errors)


class RegisterWithVerificationView(APIView):
    """
    带验证码的用户注册视图
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterWithVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return success_response(msg="注册成功")
        
        return error_response(msg=serializer.errors)


class ResetPasswordView(APIView):
    """
    重置密码视图
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            
            # 设置新密码
            user.set_password(new_password)
            user.save()
            
            return success_response(msg="密码重置成功，请使用新密码登录")
        
        return error_response(msg=serializer.errors)
