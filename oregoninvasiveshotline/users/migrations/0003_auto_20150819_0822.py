# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150730_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='biography',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(upload_to='images', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='affiliations',
            field=models.TextField(blank=True),
        ),
    ]
