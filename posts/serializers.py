from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from users.models import User
from posts.models import Post, Plate, ManagePlate
from users.serializers import UserDescSerializer, UserBriefSerializer


# region Description

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


# endregion


# region Post


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Post serializer for post creation
    """
    tags = TagListSerializerField(required=False)
    plate = PlateDescSerializer(read_only=True)
    plate_id = serializers.IntegerField(write_only=True)
    author = UserDescSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = ('postID', 'title', 'content', 'tags', 'plate', 'plate_id', 'author', 'author_id', 'coverImg')
        read_only_fields = ('postID', 'author')

    def validated_plate_id(self, value):
        try:
            plate = Plate.objects.get(plateID=value)
            return plate
        except Plate.DoesNotExist:
            raise serializers.ValidationError("Plate does not exist")


class PostsListSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()
    plate = PlateDescSerializer()
    author = UserDescSerializer()
    content = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    collection_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('postID', 'title', 'content', 'author', 'created', 'is_essence', 'tags', 'plate', 'views', 'coverImg',
                  'like_count', 'collection_count')
        read_only_fields = ("__all__",)

    def get_content(self, obj):
        return obj.content[:20]

    def get_like_count(self, obj):
        return obj.whoLikes.count()

    def get_collection_count(self, obj):
        return obj.whoCollects.count()


class PostsDetailSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    author = UserDescSerializer(read_only=True)
    plate = PlateDescSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    collection_count = serializers.SerializerMethodField()
    plate_id = serializers.IntegerField(write_only=True, required=False)

    body_html = serializers.SerializerMethodField()
    toc_html = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = (
            'postID', 'author', 'created', 'last_modified', 'views', 'whoLikes', 'whoCollects', 'body_html', 'toc_html')

    def get_like_count(self, obj):
        return obj.whoLikes.count()

    def get_collection_count(self, obj):
        return obj.whoCollects.count()

    def get_body_html(self, obj):
        return obj.get_md()[0]

    def get_toc_html(self, obj):
        return obj.get_md()[1]


# endregion


# region Plate
class PlateListSerializer(serializers.ModelSerializer):
    moderators = serializers.SerializerMethodField()

    #  managePlates = serializers.SerializerMethodField()

    class Meta:
        model = Plate
        fields = ('plateID', 'name', 'description', 'moderators')
        read_only_fields = ("__all__",)

    def get_moderators(self, obj):
        moderators = User.objects.filter(managePlates__plate=obj)
        return UserDescSerializer(moderators, many=True).data


class PlateDetailSerializer(serializers.ModelSerializer):
    # TODO:这里重复了moderator的信息, 待前后端交接时沟通
    moderators = serializers.SerializerMethodField()
    managePlates = serializers.SerializerMethodField()

    class Meta:
        model = Plate
        fields = "__all__"
        read_only_fields = ("__all__",)

    def get_moderators(self, obj):
        moderators = User.objects.filter(managePlates__plate=obj)
        return UserDescSerializer(moderators, many=True).data

    def get_managePlates(self, obj):
        managePlates = ManagePlate.objects.filter(plate=obj)
        return ManagePlateDescSerializer(managePlates, many=True).data


class PlateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plate
        fields = "__all__"
        read_only_fields = ("plateID",)


# endregion


# region ManagePlate
class ManagePlateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagePlate
        fields = "__all__"
        read_only_fields = ("mpID", 'created')


class ManagePlateActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagePlate
        fields = ('mpID', 'plate', 'moderator', 'created')
        read_only_fields = ("__all__",)

# endregion
