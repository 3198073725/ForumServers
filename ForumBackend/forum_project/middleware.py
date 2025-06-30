"""
全局异常处理中间件
"""

from django.http import JsonResponse
import logging
import traceback

logger = logging.getLogger(__name__)

class ExceptionMiddleware:
    """
    捕获异常并确保返回正确的响应格式和CORS头
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # 记录异常信息
            logger.error(f"未捕获的异常: {str(e)}")
            logger.error(traceback.format_exc())
            
            # 创建错误响应
            error_response = JsonResponse({
                "status": 500,
                "code": 500,
                "msg": "服务器内部错误",
                "detail": str(e) if not isinstance(e, AssertionError) else "断言错误"
            }, status=500)
            
            # 添加CORS头部
            origin = request.headers.get('origin')
            if origin:
                error_response['Access-Control-Allow-Origin'] = origin
                error_response['Access-Control-Allow-Credentials'] = 'true'
            
            return error_response 