from django.apps import AppConfig


class MainAppConfig(AppConfig):

    name = 'oregoninvasiveshotline'

    def ready(self):
        # The following enables legacy ARCUtils behavior by adding a
        # bunch of default template tags. It would be better to add the
        # relevant {% load xxx %} in the templates that use these tags.
        # Django 1.9 has a new setting that "officially" enables adding
        # default tags, so we could leave this until we upgrade to 1.9.
        from django.template.base import add_to_builtins
        add_to_builtins('django.contrib.staticfiles.templatetags.staticfiles')
        add_to_builtins('bootstrapform.templatetags.bootstrap')
        add_to_builtins('arcutils.templatetags.arc')
