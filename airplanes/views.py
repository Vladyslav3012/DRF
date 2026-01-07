from .models import Airlines, Airplanes
from .serializers import AirlinesSerializer, AirplanesSerializer
from rest_framework import viewsets


class AirplanesViewSet(viewsets.ModelViewSet):
    serializer_class = AirplanesSerializer
    queryset = Airplanes.objects.all()


class AirlinesViewSet(viewsets.ModelViewSet):
    serializer_class = AirlinesSerializer
    queryset = Airlines.objects.all()
