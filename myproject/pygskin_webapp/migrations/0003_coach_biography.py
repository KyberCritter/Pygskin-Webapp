# Generated by Django 5.0.4 on 2024-05-06 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pygskin_webapp', '0002_subscriber'),
    ]

    operations = [
        migrations.AddField(
            model_name='coach',
            name='biography',
            field=models.TextField(default='', max_length=1000),
        ),
    ]
