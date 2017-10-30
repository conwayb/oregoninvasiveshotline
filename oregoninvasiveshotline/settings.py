from django.conf import global_settings

from arcutils.settings import init_settings
from arctasks.aws.processors import (set_secret_key,
                                     set_database_parameters,
                                     set_elasticsearch_kwargs)


settings = init_settings(settings_processors=[set_secret_key,
                                              set_database_parameters,
                                              set_elasticsearch_kwargs])

PASSWORD_HASHERS = list(global_settings.PASSWORD_HASHERS)
PASSWORD_HASHERS.insert(1, 'oregoninvasiveshotline.utils.RubyPasswordHasher')
