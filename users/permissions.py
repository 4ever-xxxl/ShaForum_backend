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

        # 超级管理员
        if request.user.is_superuser:
            return True

        if request.method == 'POST':
            return request.uesr.has_perm('users.change_user')

        # 用户修改或删除自己的信息
        if request.method == 'PATCH' or request.method == 'DELETE':
            return request.user == view.get_object()

        return False


class UserAvatarPermission(BasePermission):
    """
    Global permission check for user avatar.
    :description: admin has all permissions. user can view all avatars and update his own avatar.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        # 超级管理员
        if request.user.is_superuser:
            return True

        return request.user == view.get_object()