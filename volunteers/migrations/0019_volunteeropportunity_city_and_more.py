# Generated by Django 5.0.7 on 2024-11-13 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0018_user_profile_is_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteeropportunity',
            name='city',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='volunteeropportunity',
            name='country',
            field=models.CharField(default='United Kingdom', max_length=100),
        ),
        migrations.AddField(
            model_name='volunteeropportunity',
            name='county',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='volunteeropportunity',
            name='postcode',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='volunteeropportunity',
            name='street_address',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
