from rest_framework import permissions


class PostsActionPermission(permissions.BasePermission):
    """
    Global permission check for posts action
    """

    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        # 管理员可以对所有文章进行操作
        if request.user.is_superuser:
            return True

        # 所有人都可以创建文章
        if request.method == 'POST':
            return True

        # 版主可以对自己版块的文章进行操作
        if view.get_object().plate in request.user.plates:
            return True

        # 文章的作者可以修改或删除文章
        if request.method == 'PATCH' or request.method == 'DELETE':
            return request.user == view.get_object().author

        return False
