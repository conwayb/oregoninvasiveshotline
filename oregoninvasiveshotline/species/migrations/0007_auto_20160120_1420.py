# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('species', '0006_auto_20150821_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='species',
            name='is_confidential',
            field=models.BooleanField(help_text='A species can be marked as confidential if making a report about it public would cause harm', default=False),
        ),
    ]
