from rest_framework import permissions
from rest_framework.permissions import BasePermission


class UserProfilePermission(BasePermission):
    """
    Global permission check for user profile.
    :description: admin has all permissions. user can view all profiles and update his own profile.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        # 管理员可以对所有用户进行操作
        if request.user.is_superuser:
            return True

        # 用户修改或删除自己的信息
        if request.method == 'PATCH' or request.method == 'DELETE':
            return request.user == self.get_object()

        return False
