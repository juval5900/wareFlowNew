# Generated by Django 4.2.2 on 2023-09-20 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERAPP', '0008_userrole'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrole',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
