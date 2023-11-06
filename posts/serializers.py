from rest_framework import serializers
from taggit.serializers import TagListSerializerField
import random
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from users.models import User
from posts.models import Post, Plate, ManagePlate
from users.descSerializers import UserDescSerializer
from posts.descSerializers import UserDescSerializer, PlateDescSerializer, ManagePlateDescSerializer
import sys


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


class PostBaseSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()
    plate = PlateDescSerializer()
    author = UserDescSerializer()
    content = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    collect_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    has_collected = serializers.SerializerMethodField()
    coverImg = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('postID', 'title', 'content', 'author', 'created', 'is_essence', 'tags', 'plate', 'views', 'coverImg',
                  'like_count', 'collect_count', 'has_liked', 'has_collected')
        read_only_fields = ("__all__",)

    def get_content(self, obj):
        return obj.content
    
    def get_like_count(self, obj):
        return obj.whoLikes.count()
    
    def get_collect_count(self, obj):
        return obj.whoCollects.count()
    
    def get_has_liked(self, obj):
        return obj.whoLikes.filter(user_id=self.context['request'].user).exists()
    
    def get_has_collected(self, obj):
        return obj.whoCollects.filter(user_id=self.context['request'].user).exists()
    
    def get_coverImg(self, obj):
        cover_img = obj.coverImg
        request = self.context.get('request')
        if cover_img:
            return request.build_absolute_uri(cover_img.url)
        else:
            default_img_number = random.randint(1, 9)
            default_img_path = f'/api/media/covers/default-{default_img_number}.jpg'
            full_default_img_path = request.build_absolute_uri(default_img_path)
            return full_default_img_path
    



class PostsListSerializer(PostBaseSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('postID', 'title', 'content', 'author', 'created', 'is_essence', 'tags', 'plate', 'views', 'coverImg',
                  'like_count', 'collect_count', 'has_liked', 'has_collected')
        read_only_fields = ("__all__",)

    def get_content(self, obj):
        return obj.content[:100]


class PostsDetailSerializer(PostBaseSerializer):
    tags = TagListSerializerField(required=False)
    plate_id = serializers.IntegerField(write_only=True, required=False)
    body_html = serializers.SerializerMethodField()
    toc_html = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = (
            'postID', 'author', 'coverImg', 'created', 'last_modified', 'views', 'whoLikes', 'whoCollects', 'body_html',
            'toc_html')

    def get_body_html(self, obj):
        return obj.get_md()[0]

    def get_toc_html(self, obj):
        return obj.get_md()[1]
    
    def validated_plate_id(self, value):
        try:
            plate = Plate.objects.get(plateID=value)
            return plate
        except Plate.DoesNotExist:
            raise serializers.ValidationError("Plate does not exist")


class PostCoverImgSerializer(PostBaseSerializer):
    class Meta:
        model = Post
        fields = ('postID', 'coverImg',)
        read_only_fields = ('postID',)

    def save(self, **kwargs):
        post = super().save(**kwargs)
        
        # 对上传的图片进行压缩
        if post.coverImg:
            img = Image.open(post.coverImg)
            output = BytesIO()
            img.save(output, format='JPEG', quality=70)
            output.seek(0)
            post.coverImg = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % post.coverImg.name.split('.')[0],
                                                'image/jpeg', sys.getsizeof(output), None)
        post.save()
        return post


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
