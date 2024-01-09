# Generated by Django 4.2.2 on 2023-07-01 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0012_remove_post_comments_comments_post'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comments',
            old_name='body',
            new_name='content',
        ),
        migrations.RemoveField(
            model_name='comments',
            name='post',
        ),
        migrations.AddField(
            model_name='comments',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='social.post'),
        ),
    ]
