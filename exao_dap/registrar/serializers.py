from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Dataset, Datum



class DatumInitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datum
        fields = ['filename', 'kind', 'size_bytes', 'checksum']

class RelatedDatumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datum
        fields = ['filename', 'state', 'kind', 'imported_at',
                  'created_at', 'meta', 'checksum', 'size_bytes']

class DatasetSerializer(serializers.ModelSerializer):
    data = RelatedDatumSerializer(many=True)
    shared = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='username')
    owner = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='username')

    class Meta:
        model = Dataset
        fields = ['identifier', 'friendly_name', 'source', 'owner', 'state', 'created_at',
                  'stage', 'source_path', 'data_store_path', 'data', 'shared', 'public']


class RelatedDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['identifier', 'owner', 'source', 'stage', 'public']

class DatumSerializer(serializers.ModelSerializer):
    dataset = RelatedDatasetSerializer()
    class Meta:
        model = Datum
        fields = ['filename', 'dataset', 'state', 'kind', 'imported_at',
                  'created_at', 'meta', 'checksum', 'data_store_path', 'size_bytes']

class DatasetInitSerializer(serializers.ModelSerializer):
    data = DatumInitSerializer(many=True)
    owner = serializers.SlugRelatedField(
        many=False,
        slug_field='username',
        queryset=get_user_model().objects.all()
    )

    def create(self, validated_data):
        datum_payloads = validated_data.pop('data')
        with transaction.atomic():
            dataset = Dataset(**validated_data)
            dataset.save()
            for datum in datum_payloads:
                datum = Datum(**datum)
                datum.dataset = dataset
                datum.save()
        return dataset

    class Meta:
        model = Dataset
        fields = ['identifier', 'friendly_name', 'source', 'description',
                  'stage', 'source_path', 'data', 'owner']
        depth = 1
