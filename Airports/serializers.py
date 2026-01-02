from rest_framework import serializers
from .models import Airports, Country

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"
        read_only_fields = ['id']

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airports
        fields = "__all__"
        read_only_fields = ['id']