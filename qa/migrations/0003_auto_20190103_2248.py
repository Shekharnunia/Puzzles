# Generated by Django 2.1.4 on 2019-01-03 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0002_auto_20190103_2016'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['total_votes', '-timestamp'], 'verbose_name': 'Question', 'verbose_name_plural': 'Questions'},
        ),
    ]