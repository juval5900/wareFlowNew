# Generated by Django 4.2.2 on 2023-09-09 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERAPP', '0002_orders_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_status',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='orders',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]
