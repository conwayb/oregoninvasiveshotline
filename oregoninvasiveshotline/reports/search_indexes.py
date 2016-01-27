from haystack import indexes

from .models import Report


class ReportIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)

    report_id = indexes.IntegerField(model_attr='report_id', boost=1.125)

    title = indexes.CharField(model_attr='title', boost=1.125)
    description = indexes.CharField(model_attr='description')
    location = indexes.CharField(model_attr='location')

    edrr_status = indexes.CharField(model_attr='get_edrr_status_display')
    ofpd = indexes.BooleanField(model_attr='created_by__has_completed_ofpd')

    category = indexes.CharField(model_attr='category__name', boost=1.0625)
    category_id = indexes.IntegerField(model_attr='category__pk')

    claimed_by = indexes.CharField(model_attr='claimed_by', null=True)
    claimed_by_id = indexes.IntegerField(model_attr='claimed_by__user_id', null=True)

    county = indexes.CharField(model_attr='county__name', null=True, boost=1.0625)
    county_id = indexes.IntegerField(model_attr='county__pk', null=True)

    created_by = indexes.CharField(model_attr='created_by')
    created_by_id = indexes.IntegerField(model_attr='created_by__user_id')
    created_on = indexes.DateTimeField(model_attr='created_on')

    is_archived = indexes.BooleanField(model_attr='is_archived', default=False)
    is_public = indexes.BooleanField(model_attr='is_public', default=False)

    species_id = indexes.CharField(model_attr='species__pk', null=True)
    species = indexes.CharField(model_attr='species__title', null=True, boost=1.0625)
    reported_species = indexes.CharField(model_attr='reported_species__name', null=True)
    actual_species = indexes.CharField(model_attr='actual_species__name', null=True)

    # Non-indexed fields (i.e., fields that we don't search on but that
    # we want available in search results).

    icon_url = indexes.CharField(model_attr='icon_url', indexed=False)
    image_url = indexes.CharField(model_attr='image_url', default=None, indexed=False)

    lat = indexes.FloatField(model_attr='point__y', indexed=False)
    lng = indexes.FloatField(model_attr='point__x', indexed=False)

    def get_model(self):
        return Report
