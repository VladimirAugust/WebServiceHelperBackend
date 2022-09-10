# Generated by Django 4.1 on 2022-08-17 13:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_user_block_reason_user_is_block'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_block',
        ),
        migrations.AlterField(
            model_name='user',
            name='gifts',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Дары'),
        ),
    ]