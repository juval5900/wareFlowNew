# Generated by Django 4.2.2 on 2023-10-08 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERAPP', '0014_orders_buying_price_orders_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='suppliers',
            field=models.ManyToManyField(blank=True, related_name='products', to='USERAPP.supplier'),
        ),
    ]
