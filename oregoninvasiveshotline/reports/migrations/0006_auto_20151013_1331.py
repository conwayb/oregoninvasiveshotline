# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_auto_20150826_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='edrr_status',
            field=models.IntegerField(verbose_name='EDRR Status', choices=[(None, ''), (0, 'No Response/Action Required'), (1, 'Local expert notified'), (2, 'Population assessed'), (3, 'Population treated'), (4, 'Ongoing monitoring'), (5, 'Controlled at site')], null=True, blank=True, default=None),
        ),
    ]
