# Generated by Django 4.2.2 on 2023-09-13 01:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('USERAPP', '0005_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='StorageLocation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('location_name', models.CharField(max_length=255, unique=True)),
                ('row_capacity', models.PositiveIntegerField()),
                ('column_capacity', models.PositiveIntegerField()),
                ('shelf_capacity', models.PositiveIntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='orders',
            name='is_stored',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ProductLocation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('shelf_number', models.CharField(max_length=50)),
                ('row_number', models.CharField(max_length=50)),
                ('column_number', models.CharField(max_length=50)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='USERAPP.product')),
                ('storage_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='USERAPP.storagelocation')),
            ],
        ),
    ]
