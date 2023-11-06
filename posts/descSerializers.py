from posts.models import Post, Plate, ManagePlate
from users.descSerializers import UserDescSerializer, UserBriefSerializer
from rest_framework import serializers

class PostDescSerializer(serializers.ModelSerializer):
    """
    Post serializer for post description in comments
    """

    class Meta:
        model = Post
        fields = ('postID', 'title')


class PlateDescSerializer(serializers.ModelSerializer):
    """
    Plate serializer for plate description in posts
    """

    class Meta:
        model = Plate
        fields = ('plateID', "name")


class ManagePlateDescSerializer(serializers.ModelSerializer):
    """
    Plate serializer for plate description in posts
    """
    moderator = UserDescSerializer()

    class Meta:
        model = ManagePlate
        fields = ('mpID', 'moderator', 'created')
        read_only_fields = ("__all__",)


class ManagePlateListSerializer(serializers.ModelSerializer):
    """
    Plate serializer for plate description in posts
    """
    moderator = UserBriefSerializer()
    plate = PlateDescSerializer()

    class Meta:
        model = ManagePlate
        fields = ('mpID', 'plate', 'moderator', 'created')
        read_only_fields = ("__all__",)

