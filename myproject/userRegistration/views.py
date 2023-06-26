from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from rest_framework.decorators import api_view, permission_classes, schema

from .tasks import send_welcome_email
from rest_framework.response import Response



#register api view 
@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={
        201: 'User registered successfully.',
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        send_welcome_email.apply_async(args=(user.id,), countdown=20)  # Set countdown to 10 seconds
        # send_welcome_email.apply_async(args=(user.id,), countdown=timedelta(days=1).total_seconds())
        return Response({'message': 'User registered successfully.'})
    return Response(serializer.errors, status=400)

#login api view
@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={
        201: 'User registered successfully.',
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def login(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.data)
    return Response(serializer.errors, status=400)
    