from django.db import models

class DataSet(models.Model):
    class DataSetSource(models.TextChoices):
        SIMULATION = 'simulation', 'simulation'
        LAB = 'lab', 'lab'
        ONSKY = 'onsky', 'on sky'
    source = models.CharField(
        max_length=10,
        choices=DataSetSource.choices
    )
    origin_path = models.CharField(max_length=1024)

class Datum(models.Model):
    class DatumKind(models.TextChoices):
        REF = 'ref', 'reference'
        SCI = 'sci', 'science'
        CAL = 'cal', 'calibration'
    metadata = models.JSONField()

# class Observation(models.Model):
#     pass
