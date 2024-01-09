# Generated by Django 4.1.4 on 2023-06-15 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0011_alter_post_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='comments',
        ),
        migrations.AddField(
            model_name='comments',
            name='post',
            field=models.ManyToManyField(blank=True, related_name='comments', to='social.post'),
        ),
    ]