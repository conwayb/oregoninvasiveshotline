from haystack import indexes

from .models import Species


class SpeciesIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    category = indexes.CharField(model_attr='category')
    name = indexes.CharField(model_attr='name')
    remedy = indexes.CharField(model_attr='remedy')
    resources = indexes.CharField(model_attr='resources')
    scientific_name = indexes.CharField(model_attr='scientific_name')
    severity = indexes.CharField(model_attr='severity')

    is_confidential = indexes.BooleanField(model_attr='is_confidential', indexed=False)

    def get_model(self):
        return Species

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
