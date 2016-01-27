# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_auto_20150806_1715'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ['-pk']},
        ),
        migrations.AlterField(
            model_name='report',
            name='location',
            field=models.TextField(verbose_name='Please provide a description of the area where species was found', help_text='\n            For example name the road, trail or specific landmarks\n            near the site whether the species was found. Describe the geographic\n            location, such as in a ditch, on a hillside or in a streambed. If you\n            happen to have taken GPS coordinates, enter them here.\n        '),
        ),
    ]
