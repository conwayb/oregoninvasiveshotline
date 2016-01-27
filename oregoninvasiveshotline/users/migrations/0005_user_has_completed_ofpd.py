# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_completed_ofpd',
            field=models.BooleanField(verbose_name='I have completed the Oregon Forest Pest Detector training, offered by Oregon State Extension.', default=False),
        ),
    ]
