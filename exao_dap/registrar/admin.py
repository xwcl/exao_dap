# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import DataSet, Datum


@admin.register(DataSet)
class DataSetAdmin(admin.ModelAdmin):
    list_display = (
        'identifier',
        'friendly_name',
        'source',
        'stage',
        'created_at',
        'source_path',
        'state',
        'owner',
        'public',
    )
    list_filter = ('created_at', 'owner', 'public')
    raw_id_fields = ('shared',)
    date_hierarchy = 'created_at'


@admin.register(Datum)
class DatumAdmin(admin.ModelAdmin):
    list_display = (
        'path',
        'dataset',
        'state',
        'kind',
        'imported_at',
        'created_at',
        'metadata',
    )
    list_filter = ('dataset', 'imported_at', 'created_at')
    date_hierarchy = 'created_at'
