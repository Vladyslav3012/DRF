from drf_spectacular.utils import extend_schema

from custom_permission import IsAdminOrReadOnly
from .models import Airlines, Airplanes
from .serializers import (AirlinesRetrieveSerializer,
                          AirlinesListSerializer,
                          AirplanesListSerializer,
                          AirplanesRetrieveSerializer)
from rest_framework import viewsets


@extend_schema(tags=['Airplanes'])
class AirplanesViewSet(viewsets.ModelViewSet):
    queryset = Airplanes.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return AirplanesListSerializer
        return AirplanesRetrieveSerializer


@extend_schema(tags=['Airlines'])
class AirlinesViewSet(viewsets.ModelViewSet):
    queryset = Airlines.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return AirlinesListSerializer
        return AirlinesRetrieveSerializer
