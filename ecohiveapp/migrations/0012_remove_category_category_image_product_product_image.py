# Generated by Django 4.2.4 on 2023-09-02 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecohiveapp', '0011_remove_category_product_names'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='category_image',
        ),
        migrations.AddField(
            model_name='product',
            name='product_image',
            field=models.ImageField(blank=True, null=True, upload_to='category_images/'),
        ),
    ]