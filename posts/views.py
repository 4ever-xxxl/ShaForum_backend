import django_filters
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters

from CustomPagination import CustomPagination
from posts.models import Post, Plate, LikeUserPost, CollectUserPost
from posts.serializers import PostsListSerializer, PostsDetailSerializer, PlateListSerializer, PlateDetailSerializer, \
    PostCreateSerializer, PlateDescSerializer
from posts.permissions import PostsActionPermission, PlateActionPermission


def index(request):
    return HttpResponse("Hello, world. You're at the posts backend index.")


# region Post
class PostDetailView(generics.RetrieveAPIView):
    """
     Retrieve a post instance with all details by postID.
    """
    queryset = Post.objects.all()
    serializer_class = PostsDetailSerializer

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            post.increase_views()
            serializer = PostsDetailSerializer(post)
            return JsonResponse({'status': "success", 'post': serializer.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class PostListView(generics.ListAPIView):
    """
    List all posts with simple information by filter.
    """
    pagination_class = CustomPagination
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
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class PostCreateView(generics.CreateAPIView):
    """
    Create a post instance.
    """
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

    def post(self, request, *args, **kwargs):
        try:
            cpdata = request.data.copy()
            cpdata['author_id'] = request.user.userID
            serializer = PostCreateSerializer(data=cpdata)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            new_post = Post.objects.get(postID=serializer.data['postID'])
            return JsonResponse({'status': "success", 'post': PostsDetailSerializer(new_post).data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class PostActionView(generics.RetrieveUpdateDestroyAPIView):
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
            post.increase_views()
            return JsonResponse({'status': "success", 'post': serializer.data})
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


class PostLikeView(generics.GenericAPIView):
    """
    Like or unlike a post instance by postID.
    """
    def get_object(self):
        return Post.objects.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            like_user_post, created = LikeUserPost.objects.get_or_create(user=request.user, post=post)
            if created:
                return JsonResponse({'status': "success", 'message': "like success"})
            else:
                return JsonResponse({'status': "success", 'message': "already liked"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            like_user_post = LikeUserPost.objects.get(user=request.user, post=post)
            like_user_post.delete()
            return JsonResponse({'status': "success", 'message': "unlike success"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class PostCollectView(generics.GenericAPIView):
    """
    Collect or uncollect a post instance by postID.
    """
    def get_object(self):
        return Post.objects.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            collect_user_post, created = CollectUserPost.objects.get_or_create(user=request.user, post=post)
            if created:
                return JsonResponse({'status': "success", 'message': "collect success"})
            else:
                return JsonResponse({'status': "success", 'message': "already collected"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            collect_user_post = CollectUserPost.objects.get(user=request.user, post=post)
            collect_user_post.delete()
            return JsonResponse({'status': "success", 'message': "uncollect success"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


# endregion

# region Plate
class PlateListView(generics.ListAPIView):
    pagination_class = CustomPagination
    queryset = Plate.objects.all()
    serializer_class = PlateListSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = {
        'plateID': ['exact'],
        'name': ['exact', 'contains'],
    }

    def post(self, request, *args, **kwargs):
        try:
            query_filters = Q()
            for field, value in request.data.items():
                if field in self.filter_fields:
                    lookup = f"{field}__icontains"  # 使用icontains进行部分匹配
                    query_filters &= Q(**{lookup: value})
            queryset = self.filter_queryset(self.get_queryset()).filter(query_filters)
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return JsonResponse({'status': "success", 'platelist': serializer.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class PlateDetailView(generics.RetrieveAPIView):
    queryset = Plate.objects.all()
    serializer_class = PlateListSerializer

    def get(self, request, *args, **kwargs):
        try:
            plate = self.get_object()
            serializer = PlateListSerializer(plate)
            return JsonResponse({'status': "success", 'plate': serializer.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

class PlateCreateView(generics.CreateAPIView):
    pass



class PlateActionView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [PlateActionPermission]
    queryset = Plate.objects.all()
    serializer_class = PlateDetailSerializer

    def get_object(self):
        return self.queryset.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        try:
            plate = self.get_object()
            serializer = self.get_serializer(plate)
            return JsonResponse({'status': "success", 'plate': serializer.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def patch(self, request, *args, **kwargs):
        try:
            plate = self.get_object()
            serializer = self.get_serializer(plate, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return JsonResponse({'status': "success", 'plate': serializer.data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            plate = self.get_object()
            plate.delete()
            return JsonResponse({'status': "success", 'message': "delete success"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


# endregion
