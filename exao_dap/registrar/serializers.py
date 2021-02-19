from django.db import transaction
from rest_framework import serializers
from .models import DataSet, Datum


class DatumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datum
        fields = ['path', 'state', 'kind',
                  'imported_at', 'created_at', 'metadata']


class DatumInitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datum
        fields = ['filename', 'kind']


class DataSetSerializer(serializers.ModelSerializer):
    datum_set = DatumSerializer(many=True)
    shared = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='username')
    owner = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='username')

    class Meta:
        model = DataSet
        fields = ['identifier', 'friendly_name', 'source', 'state',
                  'stage', 'source_path', 'datum_set', 'shared', 'public']
        depth = 1

class DataSetInitSerializer(serializers.ModelSerializer):
    datum_set = DatumInitSerializer(many=True, read_only=False)

    def create(self, validated_data):
        datum_set = validated_data.pop('datum_set')
        with transaction.atomic():
            dataset = DataSet.objects.create(**validated_data)
            dataset.save()
            for datum in datum_set:
                datum = Datum.objects.create(**datum)
                datum.dataset = dataset
                datum.save()
        return dataset

    class Meta:
        model = DataSet
        fields = ['identifier', 'friendly_name', 'source', 'description',
                  'stage', 'source_path', 'datum_set']
        depth = 1
