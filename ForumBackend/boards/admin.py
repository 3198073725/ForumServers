from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.template.response import TemplateResponse
from django.http import JsonResponse
from .models import Board


class BoardAdmin(admin.ModelAdmin):
    """
    板块管理界面
    """
    list_display = ('id', 'name', 'description_short', 'access_type_display', 'order', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_filter = ('access_type', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('allowed_groups', 'allowed_users')
    
    def description_short(self, obj):
        """截断描述文本"""
        if len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description
    description_short.short_description = '描述'
    
    def access_type_display(self, obj):
        """显示访问权限类型"""
        return obj.get_access_type_display()
    access_type_display.short_description = '访问权限'
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('reorder/', self.admin_site.admin_view(self.reorder_view), name='boards_board_reorder'),
        ]
        return custom_urls + urls
    
    def reorder_view(self, request):
        """板块排序视图"""
        # 处理POST请求，保存排序
        if request.method == 'POST':
            board_ids = request.POST.getlist('board_ids[]')
            for i, board_id in enumerate(board_ids):
                try:
                    board = Board.objects.get(id=board_id)
                    board.order = i
                    board.save()
                except Board.DoesNotExist:
                    pass
            return JsonResponse({'status': 'success'})
        
        # 获取所有板块，按order排序
        boards = Board.objects.all().order_by('order', 'id')
        
        # 渲染模板
        context = {
            'title': '板块排序',
            'boards': boards,
            'opts': Board._meta,
            'app_label': Board._meta.app_label,
        }
        return TemplateResponse(request, 'admin/boards/board/reorder.html', context)
    
    def changelist_view(self, request, extra_context=None):
        """添加排序按钮到列表页"""
        extra_context = extra_context or {}
        extra_context['reorder_url'] = 'admin:boards_board_reorder'
        return super().changelist_view(request, extra_context=extra_context)


# 注册模型
admin.site.register(Board, BoardAdmin)
