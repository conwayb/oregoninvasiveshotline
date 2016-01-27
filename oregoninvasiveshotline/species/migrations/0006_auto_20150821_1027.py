# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('species', '0005_auto_20150730_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='severity',
            name='color',
            field=models.CharField(validators=[django.core.validators.RegexValidator('#[0-9A-Fa-f]{6}')], help_text="An HTML color of the form '#rrggbb'", max_length=7),
        ),
        migrations.AlterField(
            model_name='species',
            name='remedy',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='species',
            name='resources',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='species',
            name='scientific_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
