# Generated by Django 4.2.2 on 2023-10-02 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controllerapp', '0007_alter_stock_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
