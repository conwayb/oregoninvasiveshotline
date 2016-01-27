# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_auto_20150821_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='edrr_status',
            field=models.IntegerField(null=True, verbose_name='EDRR Status', default=None, choices=[(None, ''), (0, 'No Response/Action Required'), (1, 'Local expert notified'), (2, 'Population assessed'), (3, 'Population treated'), (4, 'Ongoing monitoring'), (5, 'Controlled at site')]),
        ),
    ]
