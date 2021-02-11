import uuid
from django.db import models
from django.conf import settings

class DataSet(models.Model):
    # storage
    collection_path = models.CharField(primary_key=True, editable=False) # fyi iRODS collections can have really long names
    source_path = models.CharField(editable=False)

    # meta
    class DataSetSource(models.TextChoices):
        SIMULATION = 'simulation', 'simulation'
        LAB = 'lab', 'lab'
        ONSKY = 'onsky', 'on sky'
        POST = 'post', 'postprocessing'
    source = models.CharField(choices=DataSetSource.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    class State(models.TextChoices):
        NEW = 'new', 'new'
        SYNCING = 'syncing', 'syncing'
        SYNCED = 'synced', 'synced'
    state = models.CharField(choices=State.choices, default=State.NEW)
    # ways DataSets get made
    # grid = models.ForeignKey('undertaker.Grid', null=True)
    # bigjob = models.ForeignKey('undertaker.BigJob', null=True)
    # source_path = models.CharField

    # access control
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    shared = models.ManyToManyField(settings.AUTH_USER_MODEL)  # can be refreshed on demand from iRODS, should be done nightly or something
    # dependencies = models.ManyToManyField(DataSet)  # for postprocessing products, obtainable through recursive walking of grids and bigjobs but as these should be R/O it is safe to denormalize
    public = models.BooleanField()


class Datum(models.Model):
    path = models.CharField(primary_key=True, editable=False)  # want to copy in to service's storage area so backing files won't disappear, but should give read/ls access to original owner user
    dataset = models.ForeignKey(DataSet)
    class DatumKind(models.TextChoices):
        REFERENCE = 'reference', 'reference'
        SCIENCE = 'science', 'science'
        CALIBRATION = 'calibration', 'calibration'
        INTERMEDIATE = 'intermediate', 'intermediate postprocessing product'
        PRODUCT = 'product', 'high level product'
    kind = models.CharField(choices=DatumKind.choices)
    imported_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField()  # this should be inferred from metadata when available, otherwise use imported_at
    metadata = models.JSONField()

