# Generated by Django 5.0.7 on 2024-10-25 13:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0007_rename_organsation_name_organisation_organisation_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
