"""
项目通用工具函数
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
import functools
import hashlib
import json
import logging

# 获取logger
logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义异常处理
    
    参数:
        exc: 异常对象
        context: 上下文信息
        
    返回:
        Response: 自定义格式的响应
    """
    # 先调用REST framework默认的异常处理
    response = exception_handler(exc, context)

    # 如果有响应，则自定义响应格式
    if response is not None:
        # 定义标准响应格式
        custom_response_data = {
            'status': response.status_code,
            'msg': str(exc),
            'data': None
        }

        # 如果原响应中有详细错误信息，则添加到msg中
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['msg'] = response.data['detail']
            else:
                # 将原始错误信息直接传递给前端，便于前端处理字段错误
                custom_response_data['msg'] = response.data

        response.data = custom_response_data

    return response


def success_response(data=None, msg="操作成功"):
    """
    标准成功响应
    
    参数:
        data: 响应数据
        msg: 响应消息
        
    返回:
        Response: 标准格式的成功响应
    """
    response = Response({
        'status': 0,
        'msg': msg,
        'data': data
    })
    return response


def error_response(msg="操作失败", status=1, data=None):
    """
    标准错误响应
    
    参数:
        msg: 错误消息
        status: 错误状态码
        data: 错误数据
        
    返回:
        Response: 标准格式的错误响应
    """
    response = Response({
        'status': status,
        'msg': msg,
        'data': data
    })
    return response


def cache_key_generator(*args, **kwargs):
    """
    生成缓存键
    
    基于视图类名、请求路径和参数生成唯一的缓存键
    
    参数:
        *args: 位置参数
        **kwargs: 关键字参数
        
    返回:
        str: MD5格式的缓存键
    """
    # 获取视图集类名
    view_class_name = args[0].__class__.__name__
    
    # 将所有参数转换为字符串
    args_str = [str(arg) for arg in args[1:]]
    kwargs_str = [f"{k}:{v}" for k, v in sorted(kwargs.items())]
    
    # 组合所有参数
    key_parts = [view_class_name] + args_str + kwargs_str
    key_string = ":".join(key_parts)
    
    # 使用MD5生成固定长度的键，并添加前缀以区分不同类型的缓存
    prefix = getattr(args[0], '_cache_key_prefix', 'default')
    hashed_key = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"{prefix}:{hashed_key}"


def cached_view(cache_key_prefix, timeout=None):
    """
    视图函数缓存装饰器
    
    参数:
        cache_key_prefix: 缓存键前缀，通常使用视图名称
        timeout: 缓存超时时间（秒），如果为None，则使用settings.CACHE_TTL中的配置
        
    返回:
        function: 装饰后的函数
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # 获取缓存超时时间
            if timeout is None:
                ttl = getattr(settings, 'CACHE_TTL', {}).get(cache_key_prefix, 300)  # 默认5分钟
            else:
                ttl = timeout
            
            # 检查是否有自定义缓存键前缀
            self._cache_key_prefix = getattr(self, '_cache_key_prefix', cache_key_prefix)
            
            # 生成缓存键
            query_params = json.dumps(dict(request.query_params), sort_keys=True)
            user_id = request.user.id if request.user and request.user.is_authenticated else 'anonymous'
            cache_key = cache_key_generator(self, request.path, query_params, user_id)
            
            # 尝试从缓存获取
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug(f"缓存命中: {cache_key}")
                return Response(cached_data)
            
            # 执行视图函数
            logger.debug(f"缓存未命中，执行视图函数: {cache_key}")
            response = view_func(self, request, *args, **kwargs)
            
            # 如果是 DRF Response 对象，需要特殊处理
            if isinstance(response, Response):
                # 缓存响应数据
                cache_data = {
                    'data': response.data,
                    'status': response.status_code,
                    'headers': dict(response.items())
                }
                cache.set(cache_key, cache_data, ttl)
            
            return response
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    使指定模式的缓存失效
    
    参数:
        pattern: 缓存键模式，例如 'home_posts:*'
    """
    logger.debug(f"尝试使缓存失效: {pattern}")
    # 注意：这需要Redis作为缓存后端
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(pattern)
        logger.debug(f"缓存已失效: {pattern}")
    else:
        # 如果缓存后端不支持模式删除，可以在这里添加替代实现
        logger.warning(f"当前缓存后端不支持模式删除，无法使缓存失效: {pattern}")
        pass


def safe_db_operation(operation_name):
    """
    安全的数据库操作装饰器
    
    用于捕获数据库操作中的异常，并返回标准错误响应
    
    参数:
        operation_name: 操作名称，用于日志记录
        
    返回:
        function: 装饰后的函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{operation_name}时发生错误: {str(e)}", exc_info=True)
                return error_response(msg=f"操作失败: {str(e)}", status=500)
        return wrapper
    return decorator


def log_operation(operation_name):
    """
    操作日志装饰器
    
    用于记录操作日志
    
    参数:
        operation_name: 操作名称
        
    返回:
        function: 装饰后的函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"执行操作: {operation_name}, 参数: {kwargs}")
            result = func(*args, **kwargs)
            logger.info(f"操作完成: {operation_name}")
            return result
        return wrapper
    return decorator
