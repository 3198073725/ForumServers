"""
用户相关序列化器
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
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

    class Meta:
        model = User
        fields = ['username', 'email', 'nickname', 'password', 'confirm_password']
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


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            msg = '必须包含用户名和密码'
            raise serializers.ValidationError(msg, code='authorization')

        # 直接使用自定义认证后端验证
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )

        # 如果认证后端验证失败，尝试手动验证
        if not user:
            try:
                # 先尝试用户名登录
                user = User.objects.get(username=username)
                if user.check_password(password):
                    attrs['user'] = user
                    return attrs
            except User.DoesNotExist:
                pass

            try:
                # 再尝试邮箱登录
                user = User.objects.get(email=username)
                if user.check_password(password):
                    attrs['user'] = user
                    return attrs
            except User.DoesNotExist:
                pass

            # 如果所有验证方法都失败，抛出异常
            msg = '无法使用提供的凭据登录'
            raise serializers.ValidationError(msg, code='authorization')

        # 如果认证后端验证成功，返回用户
        attrs['user'] = user
        return attrs


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'avatar_url', 'role', 'created_at', 'last_login']
        read_only_fields = ['id', 'username', 'email', 'role', 'created_at', 'last_login']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户信息更新序列化器
    """
    class Meta:
        model = User
        fields = ['nickname', 'avatar_url']


class PasswordChangeSerializer(serializers.Serializer):
    """
    密码修改序列化器
    """
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        # 验证两次密码是否一致
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的新密码不一致"})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    密码重置请求序列化器
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("该邮箱未注册")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    密码重置确认序列化器
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        # 验证两次密码是否一致
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的新密码不一致"})

        return attrs


class UserBriefSerializer(serializers.ModelSerializer):
    """
    用户简要信息序列化器，用于帖子和评论等关联展示
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar_url']
        read_only_fields = ['id', 'username', 'nickname', 'avatar_url']
