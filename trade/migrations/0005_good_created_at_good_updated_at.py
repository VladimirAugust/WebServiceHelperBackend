# Generated by Django 4.0.1 on 2022-08-13 10:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0004_alter_good_description_alter_good_images_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='good',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='good',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
