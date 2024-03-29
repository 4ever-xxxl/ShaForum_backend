from rest_framework.permissions import BasePermission, SAFE_METHODS
from posts.models import ManagePlate


class CommentActionPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        if request.user.groups.filter(name='admin').exists():
            return True

        if ManagePlate.objects.filter(moderator=request.user, plate=view.get_object().post.plate).exists():
            return True

        if request.user == view.get_object().author:
            return True

        return False

