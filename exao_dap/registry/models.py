import uuid
from django.db import models

class DataSet(models.Model):
    # storage
    collection_path = models.CharField(primary_key=True, editable=False) # fyi iRODS collections can have really long names

    # meta
    class DataSetSource(models.TextChoices):
        SIMULATION = 'simulation', 'simulation'
        LAB = 'lab', 'lab'
        ONSKY = 'onsky', 'on sky'
        POST = 'post', 'postprocessing'
    source = models.CharField(choices=DataSetSource.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    # ways DataSets get made
    # grid = models.ForeignKey('undertaker.Grid', null=True)
    # bigjob = models.ForeignKey('undertaker.BigJob', null=True)
    # source_path = models.CharField

    # access control
    # owner = user
    # shared = models.ManyToManyField  # can be refreshed when source_path is avail
    # dependencies = models.ManyToManyField(DataSet)  # for postprocessing products, obtainable through recursive walking of grids and bigjobs but as these should be R/O it is safe to denormalize
    public = models.BooleanField


class Datum(models.Model):
    path = models.CharField(primary_key=True, editable=False)  # want to copy in to service's storage area so backing files won't disappear, but should give read/ls access to original owner user
    # dataset = models.ForeignKey()
    class DatumKind(models.TextChoices):
        REFERENCE = 'reference', 'reference'
        SCIENCE = 'science', 'science'
        CALIBRATION = 'calibration', 'calibration'
        INTERMEDIATE = 'intermediate', 'intermediate postprocessing product'
        PRODUCT = 'product', 'high level product'
    kind = models.CharField(choices=DatumKind.choices)
    metadata = models.JSONField()

