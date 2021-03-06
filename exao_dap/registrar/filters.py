import django_filters
from django.forms import widgets
from django_filters.widgets import RangeWidget

from .models import Datum, Dataset


class DatumFilter(django_filters.FilterSet):
    kind = django_filters.MultipleChoiceFilter(choices=Datum.DatumKind.choices, widget=widgets.CheckboxSelectMultiple())
    created_at = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD'}))
    imported_at = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD'}))
    size_bytes = django_filters.RangeFilter()
    dataset__identifier = django_filters.AllValuesMultipleFilter(
        # queryset=lambda x: Dataset.all_visible_to(x.user),
        # to_field_name='identifier'
    )
    class Meta:
        model = Datum
        fields = ['kind', 'size_bytes', 'imported_at', 'created_at']
