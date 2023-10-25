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

        # 版主可以对自己版块的文章进行操作
        if view.get_object().plate in request.user.managePlates.all():
            return True

        # 文章的作者可以修改或删除文章, 但是不能设置精华
        if request.user == view.get_object().author:
            if request.method == 'PATCH':
                return request.data.get('is_essence', None) is None
            if request.method == 'DELETE':
                return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Check if user is authenticated
        """
        # 管理员可以对所有文章进行操作
        if request.user.is_superuser:
            return True

        # 版主可以对自己版块的文章进行操作
        if obj.plate in request.user.managePlates.all():
            return True

        # 文章的作者可以修改或删除文章, 但是不能设置精华
        if request.user == obj.author:
            if request.method == 'PATCH':
                return request.data.get('is_essence', None) is None
            if request.method == 'DELETE':
                return True

        return False


class PlateActionPermission(permissions.BasePermission):
    """
    Global permission check for plate action
    """

    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        # 管理员可以对所有板块进行操作
        if request.user.is_superuser:
            return True

        # 普通管理员可以创建板块
        if request.method == 'POST':
            # return "admin" in request.user.groups.values_list('name', flat=True)
            return request.user.has_perm('posts.add_plate')

        # 版主可以对自己版块进行修改操作
        if request.method == 'PATCH':
            if request.user.has_perm('posts.change_plate'):
                return True
            else:
                return view.get_object() in request.user.managePlates.all()

        # 管理员可以删除板块
        if request.method == 'DELETE':
            return request.user.has_perm('posts.delete_plate')

        return False


class ManagePlateActionPermission(permissions.BasePermission):
    """
    Global permission check for manage plate action
    """
    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        # 管理员可以对所有板块进行操作
        if request.user.is_superuser:
            return True

        if request.method == 'POST':
            return request.user.has_perm('posts.add_manageplate')

        if request.method == 'PATCH':
            return request.user.has_perm('posts.change_manageplate')

        if request.method == 'DELETE':
            return request.user.has_perm('posts.delete_manageplate')

        return False
