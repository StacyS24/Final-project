# Generated by Django 5.0.7 on 2024-10-27 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0011_alter_organisation_organisation_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='organisation_name',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
