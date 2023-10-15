import django_filters
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters

from posts.models import Post
from posts.serializers import PostsListSerializer, PostsDetailSerializer
from posts.permissions import PostsActionPermission


def index(request):
    return HttpResponse("Hello, world. You're at the posts backend index.")


class PostDetailView(generics.RetrieveAPIView):
    """
     Retrieve a post instance with all details by postID.
    """
    queryset = Post.objects.all()
    serializer_class = PostsDetailSerializer

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            serializer = PostsDetailSerializer(post)
            return JsonResponse({'status': "success", 'post': serializer.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class PostListView(generics.ListAPIView):
    """
    List all posts with simple information by filter.
    """
    queryset = Post.objects.all()
    serializer_class = PostsListSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = {
        'postID': ['exact'],
        'title': ['exact', 'contains'],
        'content': ['exact', 'contains'],
        'author__userID': ['exact'],
        'author__username': ['exact', 'contains'],
        'tags__name': ['exact', 'contains'],
        'plate__plateID': ['exact'],
        'plate__name': ['exact', 'contains'],
        'is_essence': ['exact'],
    }

    def post(self, request, *args, **kwargs):
        try:
            query_filters = Q()
            for field, value in request.data.items():
                if field in self.filter_fields:
                    lookup = f"{field}__icontains"  # 使用icontains进行部分匹配
                    query_filters &= Q(**{lookup: value})
            queryset = self.filter_queryset(self.get_queryset()).filter(query_filters)
            serializer = self.get_serializer(queryset, many=True)
            return JsonResponse({'status': "success", 'postlist': serializer.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class PostActionView(generics.CreateAPIView):
    """
    Action on a post instance by postID.
    """
    queryset = Post.objects.all()
    serializer_class = PostsDetailSerializer
    permission_classes = [PostsActionPermission]

    def get_object(self):
        return self.queryset.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            serializer = PostsDetailSerializer(post)
            return JsonResponse({'status': "success", 'post': serializer.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_post = serializer.save()
            return JsonResponse({'status': "success", 'post': new_post.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def patch(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            serializer = self.get_serializer(post, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return JsonResponse({'status': "success", 'post': serializer.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            post.delete()
            return JsonResponse({'status': "success", 'message': "delete success"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})
