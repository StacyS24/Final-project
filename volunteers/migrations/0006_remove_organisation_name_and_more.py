# Generated by Django 5.0.7 on 2024-10-24 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0005_remove_organisation_user_organisation_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organisation',
            name='name',
        ),
        migrations.AddField(
            model_name='organisation',
            name='organsation_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
