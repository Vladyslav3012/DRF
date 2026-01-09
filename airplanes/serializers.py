from rest_framework import serializers
from .models import Airlines, Airplanes
from airports.models import Airports


class AirlinesListSerializer(serializers.ModelSerializer):
    airport = serializers.SlugRelatedField(
        slug_field="title",
        queryset=Airports.objects.all()
    )

    class Meta:
        model = Airlines
        fields = ['id', 'airport', 'title']


class AirlinesRetrieveSerializer(AirlinesListSerializer):
    airplanes = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Airlines
        fields = ['id', 'airport', 'title', 'detail', 'data_of_create',
                  'slogan', 'airplanes']


class AirplanesListSerializer(serializers.ModelSerializer):
    airlines = serializers.SlugRelatedField(
        slug_field="title",
        queryset=Airlines.objects.all()
    )

    class Meta:
        model = Airplanes
        fields = ['model', 'total_seats',
                  'airlines']


class AirplanesRetrieveSerializer(AirplanesListSerializer):
    economy_class_seats = serializers.IntegerField(min_value=0, max_value=200, default=0)
    business_class_seats = serializers.IntegerField(min_value=0, max_value=200, default=0)
    first_class_seats = serializers.IntegerField(min_value=0, max_value=200, default=0)
    flights = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Airplanes
        fields = ['model', 'economy_class_seats',
                  'business_class_seats', 'first_class_seats',
                  'total_seats', 'airlines', 'flights']

    def validate(self, attrs):
        if (attrs['economy_class_seats'] + attrs['business_class_seats']
                + attrs['first_class_seats'] == 0):
            raise serializers.ValidationError("Airplane must have at least one seat")
        return attrs
