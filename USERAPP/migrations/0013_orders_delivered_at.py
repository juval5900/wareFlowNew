# Generated by Django 4.2.2 on 2023-09-30 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERAPP', '0012_userrole_is_allocated'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='delivered_at',
            field=models.DateTimeField(null=True),
        ),
    ]
