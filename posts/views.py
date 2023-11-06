from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from notifications.signals import notify
from API.CustomPagination import CustomPagination
from comments.models import Comment
from posts.models import Post, Plate, LikeUserPost, CollectUserPost, ManagePlate
from posts.permissions import (
    PostsActionPermission,
    PlateActionPermission,
    ManagePlateActionPermission,
    PostCoverImgPermission,
)
from posts.serializers import (
    PostsListSerializer,
    PostsDetailSerializer,
    PlateListSerializer,
    PlateDetailSerializer,
    PostCreateSerializer,
    PlateCreateSerializer,
    ManagePlateCreateSerializer,
    ManagePlateActionSerializer,
    PostCoverImgSerializer,
)
from posts.descSerializers import (
    PlateDescSerializer,
    ManagePlateListSerializer,
)
from comments.serializers import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentListSerializer,
)
import logging

logger = logging.getLogger("django")


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
            return JsonResponse({"status": "success", "post": serializer.data})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PostListView(generics.ListAPIView):
    """
    List all posts with simple information by filter.
    """

    pagination_class = CustomPagination
    queryset = Post.objects.all()
    serializer_class = PostsListSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = {
        "postID": ["exact"],
        "title": ["contains"],
        "content": ["contains"],
        "author__userID": ["exact"],
        "author__username": ["contains"],
        "tags__name": ["contains"],
        "plate__plateID": ["exact"],
        "plate__name": ["contains"],
        "is_essence": ["exact"],
    }

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def post(self, request, *args, **kwargs):
        try:
            query_filters = Q()
            for field, value in request.data.items():
                if field in self.filter_fields:
                    if 'contains' in self.filter_fields[field]:
                        lookup = f"{field}__icontains"
                    else:
                        lookup = f"{field}__exact"
                    query_filters &= Q(**{lookup: value})
            queryset = self.filter_queryset(self.get_queryset()).filter(query_filters)
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PostHotListView(generics.ListAPIView):
    """
    List all hot posts with simple information by filter.
    """

    pagination_class = CustomPagination
    queryset = Post.objects.all()
    serializer_class = PostsListSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return self.queryset.order_by("-views")

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})
        
class PostEssenceListView(generics.ListAPIView):
    """
    List all essence posts with simple information by filter.
    """
    
    pagination_class = CustomPagination
    queryset = Post.objects.all()
    serializer_class = PostsListSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return self.queryset.filter(is_essence=True)

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class MyPostListView(generics.ListAPIView):
    """
    List all posts posted by current user.
    """

    pagination_class = CustomPagination
    queryset = Post.objects.all()
    serializer_class = PostsListSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PostCreateView(generics.CreateAPIView):
    """
    Create a post instance.
    """

    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

    def post(self, request, *args, **kwargs):
        try:
            cpdata = request.data.copy()
            cpdata["author_id"] = request.user.userID
            serializer = PostCreateSerializer(data=cpdata)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            new_post = Post.objects.get(postID=serializer.data["postID"])
            # 通知板主
            manage_plates = ManagePlate.objects.filter(plate=new_post.plate)
            for manage_plate in manage_plates:
                moderator = manage_plate.moderator
                notify.send(
                    sender=request.user,
                    recipient=moderator,
                    verb='newPost',
                    description='发布了新的帖子',
                    target=new_post,
                )
            return JsonResponse(
                {"status": "success", "post": PostsDetailSerializer(new_post).data}
            )
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PostActionView(generics.RetrieveUpdateDestroyAPIView):
    """
    Action on a post instance by postID.
    """

    queryset = Post.objects.all()
    serializer_class = PostsDetailSerializer
    permission_classes = [PostsActionPermission]

    def get_object(self):
        return self.queryset.get(pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            serializer = PostsDetailSerializer(post)
            post.increase_views()
            return JsonResponse({"status": "success", "post": serializer.data})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def patch(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            serializer = self.get_serializer(post, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # 通知板主
            notify.send(
                sender=request.user,
                recipient=post.plate.moderator,
                verb="updatePost",
                description="更新了帖子",
                target=post,
            )
            return JsonResponse({"status": "success", "post": serializer.data})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            if request.user != post.author:
                notify.send(
                    sender=request.user,
                    recipient=post.author,
                    verb="deletePost",
                    description="删除了你的帖子",
                    target=post,
                )
            post.delete()
            return JsonResponse({"status": "success", "message": "delete success"})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PostCoverImgView(generics.GenericAPIView):
    """
    Action on a post instance's coverImg by postID.
    """

    searliazer_class = PostCoverImgSerializer
    permission_classes = [PostCoverImgPermission]

    def get_object(self):
        return Post.objects.get(pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            post_info = self.searliazer_class(post).data
            return JsonResponse({"status": "success", "post": post_info})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def post(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            serializer = self.searliazer_class(post, data=request.data)
            serializer.is_valid(raise_exception=True)
            post.coverImg.delete()
            serializer.save()
            post_info = serializer.data
            return JsonResponse({"status": "success", "post": post_info})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            post.coverImg.delete()
            post.save()
            return JsonResponse(
                {"status": "success", "message": "delete coverImg success"}
            )
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PostLikeView(generics.GenericAPIView):
    """
    Like or unlike a post instance by postID.
    """

    def get_object(self):
        return Post.objects.get(pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            like_user_post, created = LikeUserPost.objects.get_or_create(
                user=request.user, post=post
            )
            if created:
                notify.send(
                    sender=request.user,
                    recipient=post.author,
                    verb="likePost",
                    description="点赞了你的帖子",
                    target=post,
                )
                return JsonResponse({"status": "success", "message": "like success"})
            else:
                return JsonResponse({"status": "success", "message": "already liked"})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            like_user_post = LikeUserPost.objects.get(user=request.user, post=post)
            like_user_post.delete()
            return JsonResponse({"status": "success", "message": "unlike success"})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PostCollectView(generics.GenericAPIView):
    """
    Collect or uncollect a post instance by postID.
    """

    def get_object(self):
        return Post.objects.get(pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            collect_user_post, created = CollectUserPost.objects.get_or_create(
                user=request.user, post=post
            )
            if created:
                notify.send(
                    sender=request.user,
                    recipient=post.author,
                    verb="collectPost",
                    description="收藏了你的帖子",
                    target=post,
                )
                return JsonResponse({"status": "success", "message": "collect success"})
            else:
                return JsonResponse(
                    {"status": "success", "message": "already collected"}
                )
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            collect_user_post = CollectUserPost.objects.get(
                user=request.user, post=post
            )
            collect_user_post.delete()
            return JsonResponse({"status": "success", "message": "uncollect success"})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PostStatusView(generics.GenericAPIView):
    """
    Get post liked status and collected status by postID.
    """

    def get_object(self):
        return Post.objects.get(pk=self.kwargs["pk"])
    
    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            return JsonResponse({"status": "success", "post": {
                "postID": post.postID,
                "userID": request.user.userID,
                "has_liked": post.whoLikes.filter(user_id=request.user.userID).exists(),
                "has_collected": post.whoCollects.filter(user_id=request.user.userID).exists(),
            }})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


# endregion


# region Comment


class PostCommentView(generics.GenericAPIView):
    """
    Create a comment instance.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer

    def get_object(self):
        return Post.objects.get(pk=self.kwargs["pk"])

    def post(self, request, *args, **kwargs):
        try:
            cpdata = request.data.copy()
            cpdata["author"] = request.user.userID
            cpdata["post"] = self.kwargs["pk"]
            serializer = CommentCreateSerializer(data=cpdata)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            new_comment = Comment.objects.get(commentID=serializer.data["commentID"])
            # 通知帖子作者
            notify.send(
                sender=request.user,
                recipient=new_comment.post.author,
                verb="commentPost",
                description="评论了你的帖子",
                action_object=new_comment,
                target=new_comment.post,
            )
            return JsonResponse(
                {
                    "status": "success",
                    "comment": CommentDetailSerializer(new_comment).data,
                }
            )
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PostCommentListView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer

    def get_object(self):
        return Post.objects.get(pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            queryset = self.filter_queryset(self.get_queryset()).filter(post=post)
            serializer = self.get_serializer(queryset, many=True)
            return JsonResponse({"status": "success", "comments": serializer.data})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


# endregion


# region Plate
class PlateListView(generics.ListAPIView):
    pagination_class = CustomPagination
    queryset = Plate.objects.all()
    serializer_class = PlateListSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = {
        "plateID": ["exact"],
        "name": ["contains"],
    }

    def post(self, request, *args, **kwargs):
        try:
            query_filters = Q()
            for field, value in request.data.items():
                if field in self.filter_fields:
                    if 'contains' in self.filter_fields[field]:
                        lookup = f"{field}__icontains"
                    else:
                        lookup = f"{field}__exact"
                    query_filters &= Q(**{lookup: value})
            queryset = self.filter_queryset(self.get_queryset()).filter(query_filters)
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PlateDetailView(generics.RetrieveAPIView):
    queryset = Plate.objects.all()
    serializer_class = PlateDetailSerializer

    def get(self, request, *args, **kwargs):
        try:
            plate = self.get_object()
            serializer = self.get_serializer(plate)
            return JsonResponse({"status": "success", "plate": serializer.data})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PlateCreateView(generics.CreateAPIView):
    permission_classes = [PlateActionPermission]
    queryset = Plate.objects.all()
    serializer_class = PlateCreateSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = PlateCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            new_plate = Plate.objects.get(plateID=serializer.data["plateID"])
            return JsonResponse(
                {"status": "success", "plate": PlateDescSerializer(new_plate).data}
            )
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class PlateActionView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [PlateActionPermission]
    queryset = Plate.objects.all()
    serializer_class = PlateDetailSerializer

    def get_object(self):
        return self.queryset.get(pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        try:
            plate = self.get_object()
            serializer = self.get_serializer(plate)
            return JsonResponse({"status": "success", "plate": serializer.data})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def patch(self, request, *args, **kwargs):
        try:
            plate = self.get_object()
            serializer = self.get_serializer(plate, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return JsonResponse({"status": "success", "plate": serializer.data})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            plate = self.get_object()
            plate.delete()
            return JsonResponse({"status": "success", "message": "delete success"})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


# endregion


# region ManagePlate


class ManagePlateListView(generics.ListAPIView):
    pagination_class = CustomPagination
    queryset = ManagePlate.objects.all()
    serializer_class = ManagePlateListSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = {
        "mpID": ["exact"],
        "plate__plateID": ["exact"],
        "plate__name": ["contains"],
        "moderator__userID": ["exact"],
        "moderator__username": ["contains"],
    }

    def post(self, request, *args, **kwargs):
        try:
            query_filters = Q()
            for field, value in request.data.items():
                if field in self.filter_fields:
                    if 'contains' in self.filter_fields[field]:
                        lookup = f"{field}__icontains"
                    else:
                        lookup = f"{field}__exact"
                    query_filters &= Q(**{lookup: value})
            queryset = self.filter_queryset(self.get_queryset()).filter(query_filters)
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is None:
                raise Exception("page is None")
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class ManagePlateCreateView(generics.CreateAPIView):
    permission_classes = [ManagePlateActionPermission]
    queryset = ManagePlate.objects.all()
    serializer_class = ManagePlateCreateSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_manage = serializer.save()
            user = new_manage.moderator
            if user.managePlates.count() == 1:  # 如果用户原来没有管理的板块, 则将其加入moderator组
                group = Group.objects.get(name="moderator")
                user.groups.add(group)
            # 通知被任命的用户
            notify.send(
                sender=request.user,
                recipient=new_manage.moderator,
                verb="moderator",
                description="成为了板主",
                target=new_manage.plate,
            )
            return JsonResponse(
                {
                    "status": "success",
                    "manage_plate": ManagePlateListSerializer(new_manage).data,
                }
            )
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


class ManagePlateActionView(generics.RetrieveDestroyAPIView):
    permission_classes = [ManagePlateActionPermission]
    queryset = ManagePlate.objects.all()
    serializer_class = ManagePlateActionSerializer

    def get_object(self):
        return self.queryset.get(pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        try:
            manage_plate = self.get_object()
            serializer = self.get_serializer(manage_plate)
            return JsonResponse({"status": "success", "manage_plate": serializer.data})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            manage_plate = self.get_object()
            user = manage_plate.moderator
            manage_plate.delete()
            if user.managePlates.count() == 0:  # 如果删除后用户没有管理的板块了, 则将其从moderator组中移除
                group = Group.objects.get(name="moderator")
                user.groups.remove(group)
            # 通知被撤销的用户
            notify.send(
                sender=request.user,
                recipient=user,
                verb="removeModerator",
                description="被撤销了板主",
                target=manage_plate.plate,
            )
            return JsonResponse({"status": "success", "message": "delete success"})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)})


# endregion
