# Generated by Django 4.2.4 on 2023-09-01 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecohiveapp', '0008_application_applicationstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Is admin'),
        ),
    ]
