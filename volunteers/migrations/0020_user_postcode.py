# Generated by Django 5.0.7 on 2024-11-29 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0019_volunteeropportunity_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='postcode',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
    ]
