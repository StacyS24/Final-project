# Generated by Django 5.0.7 on 2025-03-17 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0027_badges_awardbadge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='website_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
