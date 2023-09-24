# Generated by Django 4.2.2 on 2023-09-21 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('warehouse_name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('num_sectors', models.PositiveIntegerField()),
                ('manager_allocated', models.BooleanField()),
                ('controller_allocated', models.BooleanField()),
            ],
        ),
    ]
