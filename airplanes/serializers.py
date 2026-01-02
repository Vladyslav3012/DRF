from rest_framework import serializers
from .models import Airlines, Airplanes

class AirplanesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplanes
        fields = "__all__"
        read_only_fields = ['id']


class AirlinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airlines
        fields = "__all__"
        read_only_fields = ['id']