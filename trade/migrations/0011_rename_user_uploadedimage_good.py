# Generated by Django 4.0.1 on 2022-08-22 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0010_remove_good_images'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uploadedimage',
            old_name='user',
            new_name='good',
        ),
    ]
