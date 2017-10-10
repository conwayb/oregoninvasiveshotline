import hashlib
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.hashers import BasePasswordHasher, constant_time_compare
from django.contrib.sites.models import Site
from django.db.models import Q

from PIL import Image


log = logging.getLogger(__name__)


# The sites framework is dumb. I don't want to hardcode the hostname of the
# site in the database. To avoid doing that, we monkey patch
# Site.objects.get_current so it uses our custom function that always returns a
# Site object with the proper domain
def get_current(request=None, _get_current=Site.objects.get_current):
    if request is not None:
        # fake a Site object, since we are too lazy to keep the database updated
        return Site(domain=request.get_host(), name=request.get_host(), pk=getattr(settings, "SITE_ID", 1))
    else:
        return _get_current(request)

Site.objects.get_current = get_current


def generate_thumbnail(input_path, output_path, width, height):
    """Generate a thumbnail from the source image.

    If the input image is already smaller than ``width`` X ``height``,
    it will be returned as is.

    The aspect ratio will be preserved if the image has to be resized.

    If the input and output paths are the same, a ``ValueError`` will
    be raised.

    On successful thumbnail generation, ``True`` will be returned. If
    the thumbnail can't be generated for some reason, ``False`` will be
    returned.

    """
    if input_path == output_path:
        raise ValueError('Input path is identical to output path')

    try:
        img = Image.open(input_path)
    except FileNotFoundError:
        log.error('Could not find image at: %s', input_path)
        return False
    except IOError:
        log.exception('Error while opening image at: %s', input_path)
        return False

    try:
        img.thumbnail((width, height))
        img.save(output_path)
    except IOError:
        log.exception('Cannot resize image at: %s', input_path)
        return False

    return True


def get_tab_counts(user, report_ids):
    from .reports.models import Report, Invite
    from .notifications.models import UserNotificationQuery
    return {
        "subscribed": UserNotificationQuery.objects.filter(user_id=user.pk).count(),
        "invited_to": Invite.objects.filter(user_id=user.pk).count(),
        "reported": Report.objects.filter(Q(pk__in=report_ids) | Q(created_by_id=user.pk)).count(),
        "open_and_claimed": 0 if user.is_anonymous() else
        Report.objects.filter(claimed_by_id=user.pk, is_public=False, is_archived=False).count(),
        "claimed_by_me": 0 if user.is_anonymous() else
        Report.objects.filter(claimed_by_id=user.pk).count(),
        "unclaimed_reports": Report.objects.filter(
            claimed_by=None,
            is_public=False,
            is_archived=False
        ).count() if user.is_authenticated() and user.is_active else 0,
    }


# Monkey patch the PasswordResetForm so it doesn't just silently ignore people
# with unusable password. Anyone with an is_active account should be able to
# reset their password
def get_users(self, email):
    return get_user_model()._default_manager.filter(email__iexact=email, is_active=True)

PasswordResetForm.get_users = get_users


class RubyPasswordHasher(BasePasswordHasher):
    """
    A password hasher that re-hashes the passwords from the old site so they can be used here.
    Encryption (old): Sha256
    """
    algorithm = "RubyPasswordHasher"

    def verify(self, password, encoded):
        """
        Actually, I think the only thing we have to do here is check that
        encoded_2 == encrypted
        instead of password == encrypted
        """
        algorithm, _, _, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        # here's the extra step
        hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return constant_time_compare(hash, hashed)
