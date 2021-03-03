from django.contrib import admin
from .models import Dataset, Datum


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = (
        'identifier',
        'friendly_name',
        'description',
        'source',
        'stage',
        'created_at',
        'source_path',
        'owner',
        'public',
    )
    list_filter = ('created_at', 'owner', 'public')
    raw_id_fields = ('shared',)
    date_hierarchy = 'created_at'


@admin.register(Datum)
class DatumAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'filename',
        'checksum',
        'dataset',
        'state',
        'kind',
        'imported_at',
        'created_at',
        'meta',
    )
    list_filter = ('dataset', 'imported_at', 'created_at')
    date_hierarchy = 'created_at'
