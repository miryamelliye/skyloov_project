# Generated by Django 4.2.2 on 2023-06-23 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_cartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='', null=True, upload_to='product_images/'),
        ),
    ]
