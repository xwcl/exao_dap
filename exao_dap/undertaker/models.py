from django.db import models

class Grid(models.Model):
    # how to specify inputs?
    inputs_spec = models.JSONField()
    params_spec = models.JSONField()
    container = models.CharField()
    nickname = models.CharField()

class BigJob(models.Model):
    grid = models.ForeignKey(Grid, null=True)
    class BigJobState(models.TextChoices):
        WAITING = 'waiting', 'waiting'
        STAGE_IN = 'stage_in', 'stage in'
        RUNNING = 'running', 'running'
        STAGE_OUT = 'stage_out', 'stage out'
        FAILED = 'failed', 'failed'
    state = models.CharField(choices=BigJobState.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    destination_dataset = models.ForeignKey('registrar.DataSet')
    # how to specify inputs?
    inputs_spec = models.JSONField()
