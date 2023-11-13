from rest_framework import serializers
from notifications.models import Notification

from users.models import User
from posts.models import Post, Plate, LikeUserPost, CollectUserPost
from comments.models import Comment, LikeUserComment, CollectUserComment
from users.descSerializers import UserDescSerializer
from posts.descSerializers import PostDescSerializer, PlateDescSerializer
from comments.descSerializers import CommentDescSerializer

class HomeSerializer(serializers.Serializer):
    """
    User serializer for user home
    """
    active_user_count = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()
    interact_count = serializers.SerializerMethodField()
    male_count = serializers.SerializerMethodField()
    female_count = serializers.SerializerMethodField()

    class Meta:
        fields = "__all__"
        read_only_fields = fields

    def get_active_user_count(self, obj):
        return User.objects.filter(is_active=True).count()
    
    def get_post_count(self, obj):
        return Post.objects.all().count()
    
    def get_interact_count(self, obj):
        return Comment.objects.all().count() + LikeUserPost.objects.all().count() + LikeUserComment.objects.all().count() + CollectUserPost.objects.all().count() + CollectUserComment.objects.all().count()
    
    def get_male_count(self, obj):
        return User.objects.filter(sex='男').count()
    
    def get_female_count(self, obj):
        return User.objects.filter(sex='女').count()

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    User serializer for user register
    """
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User serializer for user profile
    个人主页显示的基本信息
    """

    class Meta:
        model = User
        fields = (
            'userID', 'username', 'email', 'sex', 'avatar', 'status', 'stuID', 'college', 'major', 'birth_date', 'address',
            'phone',
            'is_active', 'is_superuser', 'groups', 'date_joined', 'last_login')
        read_only_fields = ('userID', 'username', 'email', 'is_superuser', 'date_joined', 'last_login')

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)


class UserAvatarSerializer(serializers.ModelSerializer):
    """
    User serializer for user avatar
    """

    class Meta:
        model = User
        fields = ('userID', 'avatar')


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()
    action_object = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'actor', 'verb', 'description', 'target', "action_object", 'level', 'unread', 'timestamp']
        # fields = '__all__'
        ordering = ['-unread', '-timestamp'] # 未读的在前面，按时间倒序排列
        
    def get_actor(self, obj):
        actor_object_id = str(obj.actor_object_id)
        return UserDescSerializer(User.objects.get(userID=actor_object_id)).data
    
    def get_target(self, obj):
        target_object_id = str(obj.target_object_id)
        if obj.verb in ['newPost', 'updatePost', 'deletePost', 'likePost', 'collectPost', 'commentPost']:
            if Post.objects.filter(postID=target_object_id).exists():
                return PostDescSerializer(Post.objects.get(postID=target_object_id)).data
            else:
                return {"postID": target_object_id, "title": "该帖子已被删除"}
        if obj.verb in ['moderator', 'removeModerator']:
            if Plate.objects.filter(plateID=target_object_id).exists():
                return PlateDescSerializer(Plate.objects.get(plateID=target_object_id)).data
            else:
                return {"plateID": target_object_id, "name": "该板块已被删除"}
        if obj.verb in ['replyComment', 'likeComment', 'collectComment']:
            if Comment.objects.filter(commentID=target_object_id).exists():
                return CommentDescSerializer(Comment.objects.get(commentID=target_object_id)).data
            else:
                return {"commentID": target_object_id, "content": "该评论已被删除"}
        return None
    
    def get_action_object(self, obj):
        action_object_object_id = str(obj.action_object_object_id)
        if obj.verb in ['commentPost', 'replyComment']:
            if Comment.objects.filter(commentID=action_object_object_id).exists():
                return CommentDescSerializer(Comment.objects.get(commentID=action_object_object_id)).data
            else:
                return {"commentID": action_object_object_id, "content": "该评论已被删除"}
        if obj.verb in ['likeComment', 'collectComment']:
            if Post.objects.filter(postID=action_object_object_id).exists():
                return PostDescSerializer(Post.objects.get(postID=action_object_object_id)).data
            else:
                return {"postID": action_object_object_id, "title": "该帖子已被删除"}
        return None