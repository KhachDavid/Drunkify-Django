# Generated by Django 3.1.4 on 2020-12-27 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0002_mood_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mood',
            name='user',
        ),
    ]
