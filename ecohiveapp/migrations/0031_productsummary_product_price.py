# Generated by Django 4.2.4 on 2023-09-14 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecohiveapp', '0030_productsummary_product_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsummary',
            name='product_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
