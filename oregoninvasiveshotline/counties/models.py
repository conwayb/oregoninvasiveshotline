from django.contrib.gis.db import models


class County(models.Model):

    class Meta:
        db_table = 'county'
        ordering = ['state', 'name']

    objects = models.GeoManager()

    county_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    the_geom = models.MultiPolygonField(srid=4326)

    @property
    def label(self):
        if self.state == 'Oregon':
            return self.name
        elif self.state == 'Washington':
            return '{0.name}, WA'.format(self)
        return '{0.name}, {0.state}'.format(self)

    def __str__(self):
        return self.label
