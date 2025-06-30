"""
验证码相关序列化器
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import User, VerificationCode


class SendVerificationCodeSerializer(serializers.Serializer):
    """
    发送验证码序列化器
    """
    email = serializers.EmailField(required=True)
    type = serializers.ChoiceField(
        choices=VerificationCode.TYPE_CHOICES,
        required=True
    )

    def validate_email(self, value):
        """
        验证邮箱
        """
        # 对于注册类型，验证邮箱是否已被使用
        if self.initial_data.get('type') == 'register' and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")

        # 对于重置密码类型，验证邮箱是否存在
        if self.initial_data.get('type') == 'reset_password' and not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱未注册")

        return value


class VerifyEmailSerializer(serializers.Serializer):
    """
    验证邮箱序列化器
    """
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)
    type = serializers.ChoiceField(
        choices=VerificationCode.TYPE_CHOICES,
        required=True
    )

    def validate(self, attrs):
        """
        验证验证码
        """
        email = attrs.get('email')
        code = attrs.get('code')
        type = attrs.get('type')

        # 验证验证码，但不标记为已使用
        if not VerificationCode.verify_code(email, code, type, mark_used=False):
            raise serializers.ValidationError({"code": "验证码无效或已过期"})

        return attrs


class RegisterWithVerificationSerializer(serializers.ModelSerializer):
    """
    带验证码的用户注册序列化器
    """
    # 使用password作为输入字段，但实际会存储到password_hash
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'nickname', 'password', 'confirm_password', 'code']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'nickname': {'required': False}
        }

    def validate(self, attrs):
        # 验证两次密码是否一致
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})

        # 验证用户名是否已存在
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "该用户名已被使用"})

        # 验证邮箱是否已存在
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "该邮箱已被使用"})

        # 验证验证码，在注册时标记为已使用
        code = attrs.pop('code')
        if not VerificationCode.verify_code(attrs['email'], code, 'register', mark_used=True):
            raise serializers.ValidationError({"code": "验证码无效或已过期"})

        return attrs

    def create(self, validated_data):
        # 移除确认密码字段
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        # 创建用户
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,  # 传入密码，在create_user中会设置password_hash
            nickname=validated_data.get('nickname', '')
        )

        return user


class ResetPasswordSerializer(serializers.Serializer):
    """
    重置密码序列化器
    """
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        # 验证两次密码是否一致
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})

        # 验证邮箱是否存在
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "该邮箱未注册"})

        # 验证验证码，在最终重置密码时才标记为已使用
        code = attrs.get('code')
        if not VerificationCode.verify_code(email, code, 'reset_password', mark_used=True):
            raise serializers.ValidationError({"code": "验证码无效或已过期"})

        attrs['user'] = user
        return attrs
