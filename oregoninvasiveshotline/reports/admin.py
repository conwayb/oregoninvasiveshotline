from django.contrib import admin
from django.contrib.gis.admin.options import GeoModelAdmin

from .models import Report


class CustomGeoModelAdmin(GeoModelAdmin):

    # Use a non-default URL so OpenLayers can be used over HTTPS
    openlayers_url = '//cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'


admin.site.register(Report, CustomGeoModelAdmin)
