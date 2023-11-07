from rest_framework import serializers
from notifications.models import Notification

from users.models import User
from posts.models import Post, Plate
from comments.models import Comment
from users.descSerializers import UserDescSerializer
from posts.descSerializers import PostDescSerializer, PlateDescSerializer
from comments.descSerializers import CommentDescSerializer

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
            return PostDescSerializer(Post.objects.get(postID=target_object_id)).data
        if obj.verb in ['moderator', 'removeModerator']:
            return PlateDescSerializer(Plate.objects.get(plateID=target_object_id)).data
        if obj.verb in ['replyComment', 'likeComment', 'collectComment']:
            return CommentDescSerializer(Comment.objects.get(commentID=target_object_id)).data
        return None
    
    def get_action_object(self, obj):
        action_object_object_id = str(obj.action_object_object_id)
        if obj.verb in ['commentPost', 'replyComment']:
            return CommentDescSerializer(Comment.objects.get(commentID=action_object_object_id)).data
        if obj.verb in ['likeComment', 'collectComment']:
            return PostDescSerializer(Post.objects.get(postID=action_object_object_id)).data
        return None