# Generated by Django 5.0.7 on 2025-02-20 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0025_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteeropportunity',
            name='urgent',
            field=models.BooleanField(default=False),
        ),
    ]
