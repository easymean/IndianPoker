import json
from rest_framework import status, viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.http import JsonResponse

from .models import Post
from .serializers import PostSerializer


def get_set_string(request):
    context = cache.get("posts")

    if not context:
        context = list(Post.objects.all().values("id", "text")[:5])
        context = json.dumps(context, ensure_ascii=False).encode("utf-8")
        cache.set("posts", context)

    parsed_context = json.loads(context)
    result = {"data": parsed_context}
    return JsonResponse(data=result, status=status.HTTP_200_OK)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()[:5]

    @method_decorator(cache_page(settings.CACHE_TTL))
    @method_decorator(vary_on_cookie)
    def dispatch(self, *args, **kwargs):  # middleware
        return super(PostViewSet, self).dispatch(*args, **kwargs)

    def list(self, request):
        posts = cache.get("posts")
        print(posts)
        if not posts:
            posts = Post.objects.all().values("id", "text")[:5]
            serializer = PostSerializer(posts, many=True)
            cache.set("posts", posts)

        return Response(data=posts, status=status.HTTP_200_OK)


class PostView(APIView):
    # renderer_classes = [JSONRenderer]

    @method_decorator(cache_page(settings.CACHE_TTL))
    def get(self, request, format=None):
        # posts = cache.get("posts")
        # if not posts:
        #     posts = list(Post.objects.all().values("id", "text")[:5])
        #     posts = json.dumps(posts, ensure_ascii=False).encode("utf-8")
        #     cache.set("posts", posts)
        #     print(posts)

        posts = list(Post.objects.all().values("id", "text")[:5])
        posts = json.dumps(posts, ensure_ascii=False)
        # print(posts)
        # posts = posts.encode("utf-8")
        cache.set("posts", posts)
        print(posts)
        return Response(data=posts, status=status.HTTP_200_OK)