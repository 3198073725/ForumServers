"""
用户相关工具函数
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import VerificationCode


def send_verification_email(email, code_type):
    """
    发送验证码邮件
    
    Args:
        email: 收件人邮箱
        code_type: 验证码类型，'register' 或 'reset_password'
    
    Returns:
        tuple: (是否成功, 验证码或错误信息)
    """
    try:
        # 生成验证码
        verification = VerificationCode.generate_code(email, code_type)
        
        # 根据类型确定邮件主题和模板
        if code_type == 'register':
            subject = '【论坛系统】注册验证码'
            template = 'emails/register_verification.html'
        else:  # reset_password
            subject = '【论坛系统】密码重置验证码'
            template = 'emails/reset_password_verification.html'
        
        # 构建邮件内容
        context = {
            'code': verification.code,
            'expire_minutes': settings.VERIFICATION_CODE_EXPIRE_MINUTES
        }
        
        # 如果使用HTML模板，可以使用以下代码
        # html_message = render_to_string(template, context)
        # plain_message = strip_tags(html_message)
        
        # 简单文本邮件
        if code_type == 'register':
            message = f"""
            您好，

            您正在注册论坛系统账号，验证码为：{verification.code}

            验证码有效期为{settings.VERIFICATION_CODE_EXPIRE_MINUTES}分钟，请勿泄露给他人。

            如非本人操作，请忽略此邮件。

            论坛系统团队
            """
        else:  # reset_password
            message = f"""
            您好，

            您正在重置论坛系统账号密码，验证码为：{verification.code}

            验证码有效期为{settings.VERIFICATION_CODE_EXPIRE_MINUTES}分钟，请勿泄露给他人。

            如非本人操作，请忽略此邮件。

            论坛系统团队
            """
        
        # 发送邮件
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return True, verification.code
    except Exception as e:
        return False, str(e)
