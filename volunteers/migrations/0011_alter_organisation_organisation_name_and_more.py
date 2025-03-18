# Generated by Django 5.0.7 on 2024-10-27 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0010_alter_organisation_organisation_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='organisation_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='website_url',
            field=models.URLField(default=1),
            preserve_default=False,
        ),
    ]
