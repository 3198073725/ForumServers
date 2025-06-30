from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_remove_like_likes_post_id_cf2001_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='content_type',
            field=models.CharField(
                choices=[('post', '帖子'), ('comment', '评论')],
                default='post',
                max_length=20,
                verbose_name='内容类型'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='like',
            name='content_id',
            field=models.PositiveIntegerField(default=0, verbose_name='内容ID'),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='like',
            index=models.Index(fields=['content_type', 'content_id'], name='likes_content_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('user', 'content_type', 'content_id')},
        ),
    ] 