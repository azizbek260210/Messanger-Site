from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from django.contrib.auth.hashers import make_password
from . import serializers
from messenger import models


@api_view(['POST', 'GET'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def user_create(request):
    username = request.data.get('username')
    password = request.data.get('password')
    phone = request.data.get('phone')
    bio = ''
    email = ''
    avatar = ''
    if request.data.get('avatar'):
        avatar = request.data.get('avatar')
    if request.data.get('email'):
        email = request.data.get('email')
    if request.data.get('bio'):
        bio = request.data.get('bio')
    
    user = models.User.objects.create(
        username=username,
        password=make_password(password),
        phone=phone,
        avatar=avatar,
        email=email,
        bio=bio,
    )
    return Response({
        'created': True
    })


@api_view(['POST'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
def user_update(request):
    data = request.data
    serializer = serializers.UserSerializerUpdate(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated, ])
def group_create(request):
    name = request.data.get('name')
    avatar = request.data.get('avatar')
    description = ''
    if request.data.get('description'):
        description = request.data.get('description')

    group = models.Group.objects.create(
        name=name,
        avatar=avatar,
        description=description,
        author=request.user,
    )

    return Response({
        'created': True
    })