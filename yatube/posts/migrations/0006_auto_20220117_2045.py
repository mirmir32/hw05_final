# Generated by Django 2.2.16 on 2022-01-17 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='post/', verbose_name='Картинка'),
        ),
    ]
