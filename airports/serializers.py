from rest_framework import serializers
from .models import Airports, Country


class CountryRetrieveSerializer(serializers.ModelSerializer):
    airports = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ['id', 'title', 'capital', 'airports']


class CountryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ['id', 'title', 'capital']


class AirportListSerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(
        slug_field="title",
        queryset=Country.objects.all()
    )

    class Meta:
        model = Airports
        fields = ['id', 'title', 'country']


class AirportsRetrieveSerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(
        slug_field="title",
        queryset=Country.objects.all()
    )

    class Meta:
        model = Airports
        fields = ['id', 'title', 'address', 'contact', 'country']
