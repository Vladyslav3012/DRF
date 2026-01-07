from rest_framework import generics
from .models import CustomUser
from .serializers import CustomUserSignInSerializer
from rest_framework.response import Response
from rest_framework.request import Request


class SignUpView(generics.GenericAPIView):
    serializer_class = CustomUserSignInSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User create successful", "data": serializer.data})
        return Response(serializer.errors)