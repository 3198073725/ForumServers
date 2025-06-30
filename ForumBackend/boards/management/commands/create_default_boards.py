"""
创建默认板块的管理命令
"""

from django.core.management.base import BaseCommand
from boards.models import Board


class Command(BaseCommand):
    help = '创建默认的论坛板块'

    def handle(self, *args, **options):
        # 默认板块列表
        default_boards = [
            {
                'name': '推荐',
                'description': '推荐的热门帖子和精华内容'
            },
            {
                'name': '精选',
                'description': '精选的高质量帖子和讨论'
            },
            {
                'name': '编程',
                'description': '编程相关的讨论和问题解答'
            },
            {
                'name': '灌水',
                'description': '轻松愉快的灌水区，可以发布各种闲聊内容'
            },
            {
                'name': '公告',
                'description': '论坛公告和重要通知'
            },
            {
                'name': '技术讨论',
                'description': '各种技术相关的讨论和分享'
            },
            {
                'name': '求助',
                'description': '寻求帮助和解决问题的地方'
            },
            {
                'name': '资源分享',
                'description': '分享各种有用的资源和工具'
            }
        ]

        # 创建板块
        created_count = 0
        skipped_count = 0

        for board_data in default_boards:
            # 检查板块是否已存在
            if Board.objects.filter(name=board_data['name']).exists():
                self.stdout.write(self.style.WARNING(f"板块 '{board_data['name']}' 已存在，跳过创建"))
                skipped_count += 1
                continue

            # 创建新板块
            Board.objects.create(
                name=board_data['name'],
                description=board_data['description']
            )
            self.stdout.write(self.style.SUCCESS(f"成功创建板块 '{board_data['name']}'"))
            created_count += 1

        # 输出总结信息
        self.stdout.write(self.style.SUCCESS(f"完成! 创建了 {created_count} 个新板块，跳过了 {skipped_count} 个已存在的板块"))
