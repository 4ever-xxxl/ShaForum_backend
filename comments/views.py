from django.db.models import Q
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, \
    GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from API.CustomPagination import CustomPagination
from comments.models import Comment, LikeUserComment, CollectUserComment
from comments.serializers import CommentListSerializer, CommentCreateSerializer, CommentDetailSerializer, CommentActionSerializer
from comments.permissions import CommentActionPermission
import logging

logger = logging.getLogger('django')


# Create your views here.

class CommentListView(ListAPIView):
    """
    List all comments with pagination
    """
    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filter_fields = {
        'post': ['exact'],
        'author': ['exact'],
        'parent': ['exact'],
        'reply_to': ['exact'],
    }

    def post(self, request, *args, **kwargs):
        """
        Create a query
        """
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


class CommentCreateView(CreateAPIView):
    """
    Create a comment
    """
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, *args, **kwargs):
        """
        超过两级的评论，parent为最顶级的评论，reply_to为直接父评论的作者
        :param request:  request.data: {'content': 'xxx', 'post': 'xxx', 'parent': 'xxx'}
        :return: {'status': 'success', 'message': 'xxx'}
        """
        try:
            cpdata = request.data.copy()
            cpdata['author'] = request.user.userID
            serializer = self.get_serializer(data=cpdata)
            serializer.is_valid(raise_exception=True)
            new_comment = serializer.save()
            return JsonResponse({'status': "success", 'message': CommentDetailSerializer(new_comment).data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class CommentDetailView(RetrieveAPIView):
    """
    Retrieve a comment
    """
    queryset = Comment.objects.all()
    serializer_class = CommentDetailSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            return JsonResponse({'status': "success", 'message': CommentDetailSerializer(comment).data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class CommentActionView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a comment
    """
    queryset = Comment.objects.all()
    serializer_class = CommentActionSerializer
    permission_classes = [CommentActionPermission]

    def get(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            return JsonResponse({'status': "success", 'message': CommentDetailSerializer(comment).data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def patch(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            if request.user.userID != comment.author.userID:
                raise Exception("You are not the author of this comment")
            serializer = self.get_serializer(comment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            new_comment = serializer.save()
            return JsonResponse({'status': "success", 'message': CommentDetailSerializer(new_comment).data})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            if request.user.userID != comment.author.userID:
                raise Exception("You are not the author of this comment")
            comment.delete()
            return JsonResponse({'status': "success", 'message': "Delete successfully"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class CommentLikeView(GenericAPIView):
    """
    Like or unlike a comment
    """
    queryset = Comment.objects.all()
    serializer_class = CommentDetailSerializer

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            like_user_comment, created = LikeUserComment.objects.get_or_create(user=request.user, comment=comment)
            if created:
                return JsonResponse({'status': "success", 'message': "like success"})
            else:
                return JsonResponse({'status': "success", 'message': "already liked"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            like_user_comment = LikeUserComment.objects.get(user=request.user, comment=comment)
            like_user_comment.delete()
            return JsonResponse({'status': "success", 'message': "unlike success"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})


class CommentCollectView(GenericAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentDetailSerializer

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwarg):
        try:
            comment = self.get_object()
            collect_user_comment, created = CollectUserComment.objects.get_or_create(user=request.user, comment=comment)
            if created:
                return JsonResponse({'status': "success", 'message': "collect success"})
            else:
                return JsonResponse({'status': "success", 'message': "already collected"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            collect_user_comment = CollectUserComment.objects.get(user=request.user, comment=comment)
            collect_user_comment.delete()
            return JsonResponse({'status': "success", 'message': "uncollect success"})
        except Exception as e:
            return JsonResponse({'status': "fail", 'message': str(e)})
