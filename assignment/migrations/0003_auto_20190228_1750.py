# Generated by Django 2.1.7 on 2019-02-28 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0002_auto_20190125_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentassignment',
            name='feedback',
            field=models.TextField(blank=True, null=True),
        ),
    ]