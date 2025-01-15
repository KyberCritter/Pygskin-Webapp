# Generated by Django 5.0.4 on 2024-11-21 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pygskin_webapp', '0010_alter_bet_credits_bet_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercredit',
            name='total_credits',
            field=models.DecimalField(blank=True, decimal_places=2, default=10000.0, max_digits=7, null=True),
        ),
    ]
