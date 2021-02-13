import uuid
import os
from django.db import models
from django.conf import settings
from .. import cyverse

# fyi iRODS collections can have really long names
MAX_SUPPORTED_PATH_LENGTH = 2048
MAX_IDENTIFIER_LENGTH = 128
PATH_BASE = os.path.join(cyverse.IRODS_HOME, 'registrar')

class DataSet(models.Model):
    # storage
    identifier = models.CharField(max_length=MAX_IDENTIFIER_LENGTH, primary_key=True, editable=False)

    # meta
    friendly_name = models.CharField(max_length=MAX_IDENTIFIER_LENGTH)
    class DataSetSource(models.TextChoices):
        ONSKY = 'onsky', 'on sky'
        LAB = 'lab', 'lab'
        SIMULATION = 'simulation', 'simulation'
        POST = 'post', 'postprocessed'
    source = models.CharField(max_length=10, choices=DataSetSource.choices, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # ways DataSets get made
    # grid = models.ForeignKey('undertaker.Grid', null=True)
    # bigjob = models.ForeignKey('undertaker.BigJob', null=True)
    source_path = models.CharField(max_length=MAX_SUPPORTED_PATH_LENGTH, null=True, editable=False)

    # access control
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner')
    shared = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared')  # can be refreshed on demand from iRODS, should be done nightly or something
    # dependencies = models.ManyToManyField(DataSet)  # for postprocessing products, obtainable through recursive walking of grids and bigjobs but as these should be R/O it is safe to denormalize
    public = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['identifier', 'owner'], name='unique_collection_path')
        ]

    def collection_path(self):
        return os.path.join(PATH_BASE, self.owner.username, self.identifier)


class Datum(models.Model):
    path = models.CharField(max_length=MAX_SUPPORTED_PATH_LENGTH, primary_key=True, editable=False)  # want to copy in to service's storage area so backing files won't disappear, but should give read/ls access to original owner user
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    class State(models.TextChoices):
        NEW = 'new', 'new'
        SYNCING = 'syncing', 'syncing'
        SYNCED = 'synced', 'synced'
    state = models.CharField(max_length=10, choices=State.choices, default=State.NEW)
    class DatumKind(models.TextChoices):
        SCIENCE = 'science', 'science'
        CALIBRATION = 'calibration', 'calibration'
        REFERENCE = 'reference', 'reference'
    kind = models.CharField(max_length=20, choices=DatumKind.choices)
    imported_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(null=True)  # this should be inferred from metadata when available, otherwise use imported_at
    metadata = models.JSONField()
