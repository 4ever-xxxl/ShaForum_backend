from rest_framework import serializers
from users.descSerializers import UserDescSerializer
from comments.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author = UserDescSerializer()
    reply_to = UserDescSerializer()
    like_count = serializers.SerializerMethodField()
    collect_count = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    has_collected = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "commentID",
            "content",
            "author",
            "post",
            "created",
            "last_modified",
            "parent",
            "reply_to",
            "like_count",
            "collect_count",
            "reply_count",
            "has_liked",
            "has_collected",
        )
        read_only_fields = ("__all__",)

    def get_like_count(self, obj):
        return obj.whoLikes.count()

    def get_collect_count(self, obj):
        return obj.whoCollects.count()

    def get_reply_count(self, obj):
        return obj.childComments.count()

    def get_has_liked(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return user in obj.whoLikes.all()
        return False

    def get_has_collected(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return user in obj.whoCollects.all()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "commentID",
            "content",
            "author",
            "post",
            "created",
            "last_modified",
            "parent",
            "reply_to",
        )
        read_only_fields = ("commentID", "created", "last_modified", "reply_to")

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        if comment.parent:
            comment.reply_to = comment.parent.author
            comment.parent = comment.parent.get_root()
        else:
            comment.reply_to = comment.post.author
        comment.save()
        return comment


class CommentListSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("__all__",)


class CommentDetailSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("__all__",)


class CommentActionSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = (
            "commentID",
            "content",
            "author",
            "post",
            "created",
            "last_modified",
            "parent",
            "reply_to",
            "like_count",
            "collect_count",
            "reply_count",
            "has_liked",
            "has_collected",
        )
        read_only_fields = (
            "commentID",
            "author",
            "post",
            "created",
            "last_modified",
            "parent",
            "reply_to",
            "like_count",
            "collect_count",
            "reply_count",
            "has_liked",
            "has_collected",
        )
