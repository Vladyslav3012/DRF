from .models import Airlines, Airplanes
from .serializers import AirlinesSerializer, AirplanesSerializer
from rest_framework import viewsets

class AirplanesAPI(viewsets.ModelViewSet):
    serializer_class = AirplanesSerializer
    queryset = Airplanes.objects.all()

class AirlinesAPI(viewsets.ModelViewSet):
    serializer_class = AirlinesSerializer
    queryset = Airlines.objects.all()
