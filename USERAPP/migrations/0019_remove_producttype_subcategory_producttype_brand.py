# Generated by Django 4.2.2 on 2023-10-25 06:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('USERAPP', '0018_remove_producttype_brand_producttype_subcategory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producttype',
            name='subcategory',
        ),
        migrations.AddField(
            model_name='producttype',
            name='brand',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='USERAPP.brand'),
        ),
    ]
