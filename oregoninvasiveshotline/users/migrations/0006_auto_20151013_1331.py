# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_has_completed_ofpd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='has_completed_ofpd',
            field=models.BooleanField(verbose_name='\n        Check this box if you have completed the Oregon\n        Forest Pest Detector training, offered by Oregon State\n        Extension.', default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(verbose_name='Is Manager (can login and manage reports)', default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(verbose_name='Is Admin (can do anything)', default=False),
        ),
    ]
