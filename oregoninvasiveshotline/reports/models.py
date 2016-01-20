import hashlib
import itertools
import os
import posixpath

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models.signals import post_init, post_save
from django.dispatch import receiver
from django.template import Context
from django.template.loader import get_template, render_to_string

from oregoninvasiveshotline.utils import generate_thumbnail
from oregoninvasiveshotline.reports.utils import generate_icon


class Report(models.Model):
    # cache the template since Django is so slow at rendering templates and NFS
    # makes it even worse
    TEMPLATE = get_template("reports/_popover.html")

    report_id = models.AutoField(primary_key=True)
    # It may seem odd to have FKs to the species AND category, but in the case
    # where the user doesn't know what species it is, we fall back to just a
    # category (with the reported_species field NULL'd out)
    reported_category = models.ForeignKey("species.Category")
    reported_species = models.ForeignKey("species.Species", null=True, default=None, related_name="+")

    description = models.TextField(verbose_name="Please provide a description of your find")
    location = models.TextField(
        verbose_name="Please provide a description of the area where species was found",
        help_text="""
            For example name the road, trail or specific landmarks
            near the site whether the species was found. Describe the geographic
            location, such as in a ditch, on a hillside or in a streambed. If you
            happen to have taken GPS coordinates, enter them here.
        """
    )
    has_specimen = models.BooleanField(default=False, verbose_name="Do you have a physical specimen?")

    point = models.PointField(srid=4326)
    county = models.ForeignKey('counties.County', null=True)

    created_by = models.ForeignKey("users.User", related_name="reports")
    created_on = models.DateTimeField(auto_now_add=True)

    claimed_by = models.ForeignKey("users.User", null=True, default=None, related_name="claimed_reports")

    # these are copied over from the original site
    edrr_status = models.IntegerField(verbose_name="EDRR Status", choices=[
        (None, '',),
        (0, 'No Response/Action Required',),
        (1, 'Local expert notified',),
        (2, 'Population assessed',),
        (3, 'Population treated',),
        (4, 'Ongoing monitoring',),
        (5, 'Controlled at site'),
    ], default=None, null=True, blank=True)

    # the actual species confirmed by an expert
    actual_species = models.ForeignKey("species.Species", null=True, default=None, related_name="reports")

    is_archived = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False, help_text="This report can be viewed by the public")

    objects = models.GeoManager()

    class Meta:
        db_table = "report"
        ordering = ['-pk']

    def __str__(self):
        if self.species:
            return str(self.species)

        return self.category.name

    def to_json(self):
        image_url = self.image_url
        return {
            "lat": self.point.y,
            "lng": self.point.x,
            "icon": self.icon_url,
            "title": str(self),
            "image_url": image_url,
            "content": self.__class__.TEMPLATE.render(Context({
                "report": self,
                "image_url": image_url,
            })),
        }

    @property
    def icon_color(self):
        return '#999' if self.species is None else self.species.severity.color

    @property
    def icon_rel_path(self):
        """Generate relative icon path.

        This path can be joined to ``MEDIA_ROOT`` or ``MEDIA_URL``.

        Generally, you'd use :meth:`icon_path` or :meth:`icon_url`
        instead of this.

        """
        category = self.category
        key_parts = [category.icon.path if category.icon else '', self.icon_color]
        key = '|'.join(str(p) for p in key_parts)
        key = hashlib.md5(key.encode('utf-8')).hexdigest()
        path = os.path.join('generated_icons', '%s.png' % key)
        return path

    @property
    def icon_path(self):
        """Path to (generated) icon for this report."""
        return os.path.join(settings.MEDIA_ROOT, self.icon_rel_path)

    @property
    def icon_url(self):
        """Get icon URL for this report.

        The icon is composed of a background color based on the species'
        severity and an image from the species' category. If the icon
        doesn't exist on disk, it will be created.

        If you are going to change the design or size of the icon, you
        will need to update the ``generateIcon`` function in
        ``static/js/main.js`` also.

        """
        return posixpath.join(settings.MEDIA_URL, self.icon_rel_path)

    def generate_icon(self):
        """Generate a map-style icon for this Report.

        The file path for the generated icon is based on parameters that
        will change the appearance of the icon. This ensures the icon is
        updated if the Report's category changes. The implementation of
        this logic is in :meth:`icon_rel_path`.

        """
        if not os.path.exists(self.icon_path):
            generate_icon(self.icon_path, self.category.icon, self.icon_color)

    @property
    def image_url(self):
        """
        Returns the URL to the thumbnail generated for the first public image
        attached to this report or None.

        If the thumbnail doesn't exist, it is created
        """
        for image in itertools.chain(self.image_set.all(), *(comment.image_set.all() for comment in self.comment_set.all())):
            if image.visibility == image.PUBLIC:
                output_path = os.path.join(settings.MEDIA_ROOT, "generated_thumbnails", str(image.pk) + ".png")
                if not os.path.exists(output_path):
                    generate_thumbnail(image.image.path, output_path, width=64, height=64)
                return settings.MEDIA_URL + os.path.relpath(output_path, settings.MEDIA_ROOT)

        return None

    @property
    def species(self):
        """
        Returns the actual species if it exists, and falls back on the reported_species
        """
        return self.actual_species or self.reported_species

    @property
    def category(self):
        """
        Returns the Category of the actual species, falling back to the reported_category
        """
        return self.actual_species.category if self.actual_species else self.reported_category

    @property
    def is_misidentified(self):
        """
        Returns True if the reported_species differs from the actual species (and both fields are filled out)
        """
        return bool(self.reported_species and self.actual_species and self.reported_species != self.actual_species)


@receiver([post_save, post_init], sender=Report)
def receiver__generate_icon(sender, instance, **kwargs):
    """Generate icon for Report on save and init.

    If the Report is new (does not have a PK), we skip icon generation
    here because it will either fail or generate an incorrect icon.

    """
    if instance.pk is not None:
        instance.generate_icon()


class Invite(models.Model):
    """
    Abitrary people can be invited (via email) to leave comments on a report
    """
    invite_id = models.AutoField(primary_key=True)
    # the person invited (a User object will be created for them)
    user = models.ForeignKey("users.User", related_name="invites")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("users.User", related_name="+")
    report = models.ForeignKey(Report)

    class Meta:
        db_table = "invite"

    @classmethod
    def create(cls, *, email, report, inviter, message, request):
        """
        Create and send an invitation to the person with the given email address

        Returns True if the invite was sent, otherwise False (meaning the user
        has already been invited before)
        """
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email__iexact=email)
        except user_model.DoesNotExist:
            user = user_model.objects.create(email=email, is_active=False)

        if Invite.objects.filter(user=user, report=report).exists():
            return False

        invite = Invite(user=user, created_by=inviter, report=report)

        send_mail(
            "Invasive Species Hotline Submission Review Request",
            render_to_string("reports/_invite_expert.txt", {
                "inviter": inviter,
                "message": message,
                "url": user.get_authentication_url(request, next=reverse("reports-detail", args=[report.pk]))
            }),
            "noreply@pdx.edu",
            [email]
        )

        invite.save()
        return True