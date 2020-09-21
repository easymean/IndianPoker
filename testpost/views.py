from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.core.cache import cache


@api_view(['GET'])
def get_string(request, key):
    if request.method == 'GET':
        text = cache.get(key)
        result = {key: text}
        return Response(data=result, status=status.HTTP_200_OK)


@api_view(['POST'])
def set_string(request, key, text):
    if request.method == 'POST':
        cache.set(key, text)
        return Response(data={"msg": "success"}, status=status.HTTP_200_OK)
