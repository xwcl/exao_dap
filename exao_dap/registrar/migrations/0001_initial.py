# Generated by Django 3.1.5 on 2021-02-18 16:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('identifier', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('friendly_name', models.CharField(max_length=128)),
                ('source', models.CharField(choices=[('onsky', 'On sky'), ('lab', 'Lab'), ('simulation', 'Simulation')], max_length=10)),
                ('stage', models.CharField(choices=[('raw', 'Raw'), ('calibrated', 'Calibrated'), ('reduced', 'Reduced')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('source_path', models.CharField(max_length=2048, null=True)),
                ('state', models.CharField(choices=[('ingesting', 'ingesting'), ('awaiting_commit', 'awaiting commit'), ('committed', 'committed'), ('ingesting_from_platform', 'ingesting from platform')], max_length=30)),
                ('public', models.BooleanField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL)),
                ('shared', models.ManyToManyField(blank=True, related_name='shared', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Datum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=2048, unique=True)),
                ('state', models.CharField(choices=[('new', 'new'), ('syncing', 'syncing'), ('synced', 'synced')], default='new', max_length=10)),
                ('kind', models.CharField(choices=[('science', 'science'), ('calibration', 'calibration'), ('reference', 'reference')], max_length=20)),
                ('imported_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('metadata', models.JSONField(blank=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registrar.dataset')),
            ],
        ),
        migrations.AddConstraint(
            model_name='dataset',
            constraint=models.UniqueConstraint(fields=('identifier', 'owner'), name='unique_collection_path'),
        ),
    ]
