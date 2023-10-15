from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from posts.models import Post, Plate
from users.serializers import UserDescSerializer


class PlateDescSerializer(serializers.ModelSerializer):
    """
    Plate serializer for plate description in posts
    """
    class Meta:
        model = Plate
        fields = ('plateID', "name")


class PostsListSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()
    plate = PlateDescSerializer()
    author = UserDescSerializer()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('postID', 'title', 'content', 'author', 'created', 'is_essence', 'tags', 'plate')

    def get_content(self, obj):
        return obj.content[:20]


class PostsDetailSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()
    author = UserDescSerializer()
    plate = PlateDescSerializer()

    class Meta:
        model = Post
        fields = "__all__"



