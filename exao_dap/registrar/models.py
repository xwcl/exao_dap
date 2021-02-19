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
    identifier = models.CharField(max_length=MAX_IDENTIFIER_LENGTH, primary_key=True)

    # meta
    friendly_name = models.CharField(max_length=MAX_IDENTIFIER_LENGTH)
    description = models.TextField(blank=True, default='')
    class DataSetSource(models.TextChoices):
        ONSKY = 'onsky', 'On sky'
        LAB = 'lab', 'Lab'
        SIMULATION = 'simulation', 'Simulation'
    source = models.CharField(max_length=10, choices=DataSetSource.choices)
    class DataSetStage(models.TextChoices):
        RAW = 'raw'
        CALIBRATED = 'calibrated'
        REDUCED = 'reduced'
    stage = models.CharField(max_length=10, choices=DataSetStage.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    # ways DataSets get made
    # grid = models.ForeignKey('undertaker.Grid', null=True)
    # bigjob = models.ForeignKey('undertaker.BigJob', null=True)
    source_path = models.CharField(max_length=MAX_SUPPORTED_PATH_LENGTH, null=True)
    class DataSetState(models.TextChoices):
        # user submission:
        # ingesting -> awaiting_commit -> committed
        # platform stage out:
        # ingesting_from_platform -> committed
        INGESTING = 'ingesting', 'ingesting'
        AWAITING_COMMIT = 'awaiting_commit', 'awaiting commit'
        COMMITTED = 'committed', 'committed'
        INGESTING_FROM_PLATFORM = 'ingesting_from_platform', 'ingesting from platform'
    state = models.CharField(max_length=30, choices=DataSetState.choices, default=DataSetState.INGESTING)

    # access control
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner')
    shared = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared', blank=True)  # can be refreshed on demand from iRODS, should be done nightly or something
    # dependencies = models.ManyToManyField(DataSet)  # for postprocessing products, obtainable through recursive walking of grids and bigjobs but as these should be R/O it is safe to denormalize
    public = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['identifier', 'owner'], name='unique_collection_path')
        ]

    def collection_path(self):
        return os.path.join(PATH_BASE, self.owner.username, self.identifier)

    def __str__(self):
        return f'/datasets/{self.pk}/'

class Datum(models.Model):
    # want to copy in to service's storage area so backing files won't disappear, but should give read/ls access to original owner user
    path = models.CharField(max_length=MAX_SUPPORTED_PATH_LENGTH, unique=True)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    class DatumState(models.TextChoices):
        NEW = 'new', 'new'
        SYNCING = 'syncing', 'syncing'
        SYNCED = 'synced', 'synced'
    state = models.CharField(max_length=10, choices=DatumState.choices, default=DatumState.NEW)
    class DatumKind(models.TextChoices):
        SCIENCE = 'science', 'science'
        CALIBRATION = 'calibration', 'calibration'
        REFERENCE = 'reference', 'reference'
    kind = models.CharField(max_length=20, choices=DatumKind.choices)
    imported_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(null=True)  # this should be inferred from metadata when available, otherwise use imported_at
    metadata = models.JSONField(blank=True)
