# Generated by Django 2.1.2 on 2018-12-31 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20190101_0014'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='description',
            new_name='content',
        ),
    ]
