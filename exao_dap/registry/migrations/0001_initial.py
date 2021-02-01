# Generated by Django 3.1.5 on 2021-01-31 22:26

import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('simulation', 'simulation'), ('lab', 'lab'), ('onsky', 'on sky')], max_length=10)),
                ('origin_path', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Datum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metadata', django.contrib.postgres.fields.hstore.HStoreField()),
            ],
        ),
    ]
