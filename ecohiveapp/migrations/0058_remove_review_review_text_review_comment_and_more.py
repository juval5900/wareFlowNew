# Generated by Django 4.2.4 on 2023-10-10 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecohiveapp', '0057_seller_certification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='review_text',
        ),
        migrations.AddField(
            model_name='review',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.PositiveIntegerField(),
        ),
    ]