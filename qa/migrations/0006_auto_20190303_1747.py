# Generated by Django 2.1.7 on 2019-03-03 12:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0005_auto_20190302_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='flag',
            field=models.ManyToManyField(blank=True, related_name='flag_answer', to=settings.AUTH_USER_MODEL),
        ),
    ]
