# Generated by Django 4.0.1 on 2022-08-22 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0007_remove_good_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='photos/%Y/%m/%d')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade.good')),
            ],
            options={
                'verbose_name': 'Фото товаров/услуг',
                'verbose_name_plural': 'Фото товаров/услуг',
            },
        ),
    ]
