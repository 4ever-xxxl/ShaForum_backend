from rest_framework import serializers
from users.models import User

class UserDescSerializer(serializers.ModelSerializer):
    """
    User serializer for user description in other models
    """

    class Meta:
        model = User
        fields = ('userID', 'username', 'status', 'avatar')
        read_only_fields = ('userID', 'username', 'status', 'avatar')


class UserBriefSerializer(serializers.ModelSerializer):
    """
    User serializer for user description in other models
    """

    class Meta:
        model = User
        fields = ('userID', 'username')
        read_only_fields = ('userID', 'username')