from django.conf import settings


def defaults(request):
    return {
        'CONTACT_EMAIL': settings.CONTACT_EMAIL,
        'GOOGLE': settings.GOOGLE,
    }
