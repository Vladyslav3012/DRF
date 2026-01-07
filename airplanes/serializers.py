from rest_framework import serializers
from .models import Airlines, Airplanes
from airports.models import Airports


class AirlinesSerializer(serializers.ModelSerializer):
    airplanes = serializers.StringRelatedField(many=True, read_only=True)
    airport = serializers.SlugRelatedField(
        slug_field="title",
        queryset=Airports.objects.all()
    )

    class Meta:
        model = Airlines
        fields = ['airport', 'title', 'detail', 'data_of_create',
                  'slogan', 'airplanes']


class AirplanesSerializer(serializers.ModelSerializer):
    airlines = serializers.SlugRelatedField(
        slug_field="title",
        queryset=Airlines.objects.all()
    )

    flights = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Airplanes
        fields = ['model', 'count_of_seats', 'airlines', 'flights']
