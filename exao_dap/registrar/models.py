
import uuid
import os
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_q.tasks import async_task

from .. import cyverse

# fyi iRODS collections can have really long names
MAX_SUPPORTED_PATH_LENGTH = 2048
MAX_IDENTIFIER_LENGTH = 128
HASH_LENGTH = 32  # md5 hexdigest
PATH_BASE = os.path.join(cyverse.IRODS_HOME, 'registrar')


class Dataset(models.Model):
    # storage
    identifier = models.CharField(
        max_length=MAX_IDENTIFIER_LENGTH,
        primary_key=True
    )

    # meta
    friendly_name = models.CharField(max_length=MAX_IDENTIFIER_LENGTH)
    description = models.TextField(blank=True, default='')

    class DatasetSource(models.TextChoices):
        ONSKY = 'onsky', 'On sky'
        LAB = 'lab', 'Lab'
        SIMULATION = 'simulation', 'Simulation'
    source = models.CharField(max_length=10, choices=DatasetSource.choices)

    class DatasetStage(models.TextChoices):
        RAW = 'raw'
        CALIBRATED = 'calibrated'
        REDUCED = 'reduced'
    stage = models.CharField(max_length=10, choices=DatasetStage.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class DatasetState(models.TextChoices):
        PENDING = 'pending'
        COMPLETE = 'finalized'
    state = models.CharField(
        max_length=10,
        choices=DatasetState.choices,
        default=DatasetState.PENDING
    )

    # ways Datasets get made
    # grid = models.ForeignKey('undertaker.Grid', null=True)
    # bigjob = models.ForeignKey('undertaker.BigJob', null=True)
    source_path = models.CharField(max_length=MAX_SUPPORTED_PATH_LENGTH)

    # access control
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE, related_name='datasets_owned')
    # can be refreshed on demand from iRODS, should be done nightly or something
    shared = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='datasets_shared', blank=True)
    # dependencies = models.ManyToManyField(Dataset)  # for postprocessing products, obtainable through recursive walking of grids and bigjobs but as these should be R/O it is safe to denormalize
    public = models.BooleanField(default=False)

    def data_store_path(self):
        return f'irods://{cyverse.IRODS_HOST}' + os.path.join(PATH_BASE, self.identifier)

    def __str__(self):
        return self.data_store_path()

    def data_pending(self):
        return self.datum_set.exclude(state=Datum.DatumState.SYNCED)

    @classmethod
    def all_visible_to(cls, user):
        qs = cls.objects.filter(public=True)
        if user.is_authenticated and user.is_active:
            # superusers: everything
            if user.is_superuser or user.is_staff:
                return cls.objects.all()
            # normal users: things shared with them or owned by them
            return (qs |
                    cls.objects.filter(owner=user) |
                    cls.objects.filter(shared=user))
        return qs

    def is_visible_to(self, user):
        if self.public:
            return True
        elif user.is_authenticated and user.is_active:
            if user.is_superuser or user.is_staff:
                return True
            elif self.owner == user or user.datasets_shared.filter(pk=self.pk).exists():
                return True
        return False

    @classmethod
    def all_editable_by(cls, user):
        qs = cls.objects.all()
        if user.is_authenticated and user.is_active:
            # superusers: everything
            if user.is_superuser or user.is_staff:
                return cls.objects.all()
            # normal users: things shared with them or owned by them
            return cls.objects.filter(owner=user)
        return cls.objects.none()

    def is_editable_by(self, user):
        if user.is_authenticated and user.is_active:
            if user.is_superuser or user.is_staff:
                return True
            elif self.owner == user:
                return True
        return False



class Datum(models.Model):
    # want to copy in to service's storage area so backing files won't disappear, but should give read/ls access to original owner user
    filename = models.CharField(max_length=MAX_IDENTIFIER_LENGTH)
    checksum = models.CharField(max_length=HASH_LENGTH)
    size_bytes = models.PositiveBigIntegerField(verbose_name='size (bytes)')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)

    class DatumState(models.TextChoices):
        NEW = 'new', 'new'
        SYNCING = 'syncing', 'syncing'
        SYNCED = 'synced', 'synced'
    state = models.CharField(
        max_length=10, choices=DatumState.choices, default=DatumState.NEW)

    class DatumKind(models.TextChoices):
        SCIENCE = 'science', 'science'
        CALIBRATION = 'calibration', 'calibration'
        REFERENCE = 'reference', 'reference'
        PRODUCT = 'product', 'product'
    kind = models.CharField(max_length=20, choices=DatumKind.choices)
    imported_at = models.DateTimeField(auto_now_add=True)
    # this should be inferred from metadata when available, otherwise use imported_at
    created_at = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(blank=True, default=dict)

    def data_store_path(self):
        return os.path.join(self.dataset.data_store_path(), self.filename)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['dataset', 'filename'], name='unique_object_path'),
        )

    def __str__(self):
        return self.data_store_path()


@receiver(post_save, sender=Datum)
def launch_populate_metadata(sender, instance, **kwargs):
    if instance.state == Datum.DatumState.NEW:
        async_task(
            'exao_dap.registrar.tasks.populate_metadata',
            instance.pk
        )
