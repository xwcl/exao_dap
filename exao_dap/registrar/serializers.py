from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Dataset, Datum


class DatumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datum
        fields = ['filename', 'state', 'kind', 'imported_at',
                  'created_at', 'meta', 'checksum']


class DatumInitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datum
        fields = ['filename', 'kind']


class DatasetSerializer(serializers.ModelSerializer):
    datum_set = DatumSerializer(many=True)
    shared = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='username')
    owner = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='username')

    class Meta:
        model = Dataset
        fields = ['identifier', 'friendly_name', 'source', 'owner',
                  'stage', 'source_path', 'datum_set', 'shared', 'public']
        depth = 1


class DatasetInitSerializer(serializers.ModelSerializer):
    datum_set = DatumInitSerializer(many=True)
    owner = serializers.SlugRelatedField(
        many=False,
        slug_field='username',
        queryset=get_user_model().objects.all()
    )

    def create(self, validated_data):
        datum_set = validated_data.pop('datum_set')
        with transaction.atomic():
            dataset = Dataset(**validated_data)
            dataset.save()
            for datum in datum_set:
                datum = Datum(**datum)
                datum.dataset = dataset
                datum.save()
        return dataset

    class Meta:
        model = Dataset
        fields = ['identifier', 'friendly_name', 'source', 'description',
                  'stage', 'source_path', 'datum_set', 'owner']
        depth = 1
