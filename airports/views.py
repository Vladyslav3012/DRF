from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Airports, Country
from .serializers import (AirportListSerializer, AirportsRetrieveSerializer,
                          CountryListSerializer, CountryRetrieveSerializer)
from rest_framework import status, generics


class CountryRetrieveModelAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CountryRetrieveSerializer
    queryset = Country.objects.all()


class CountryListModelAPIView(generics.ListCreateAPIView):
    serializer_class = CountryListSerializer
    queryset = Country.objects.all()


class AirportsListAPIView(generics.ListCreateAPIView):
    queryset = Airports.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AirportsRetrieveSerializer
        else:
            return AirportListSerializer

class AirportsRetrieveApiView(generics.GenericAPIView):
    serializer_class = AirportsRetrieveSerializer

    def get(self, request, pk):
        airport = get_object_or_404(Airports, pk=pk)
        serializer = AirportsRetrieveSerializer(airport)
        return Response(serializer.data)

    def put(self, request, pk):
        airport = get_object_or_404(Airports, pk=pk)
        serializer = AirportsRetrieveSerializer(airport, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, pk):
        airport = get_object_or_404(Airports, pk=pk)
        airport.delete()
        return Response(status=status.HTTP_200_OK)
