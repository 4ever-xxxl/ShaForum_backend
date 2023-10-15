from rest_framework import serializers, permissions

from users.models import User


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
    """

    class Meta:
        model = User
        fields = (
            'userID', 'username', 'email', 'avatar', 'stuID', 'college', 'major', 'birth_date', 'address', 'phone',
            'is_active', 'is_superuser', 'groups', 'plates')

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)


class UserDescSerializer(serializers.ModelSerializer):
    """
    User serializer for user description in posts
    """

    class Meta:
        model = User
        fields = ('userID', 'username', 'email')
