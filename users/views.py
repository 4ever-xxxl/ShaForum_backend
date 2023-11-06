from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from users.permissions import UserProfilePermission, UserAvatarPermission
from users.serializers import UserRegisterSerializer, UserProfileSerializer, UserAvatarSerializer
from users.models import User
from API.CustomPagination import CustomPagination
import logging

logger = logging.getLogger('django')

class UserRegisterView(generics.CreateAPIView):
    """
    User register view
    
    Prameters:
        username: str (required)
        email: str (required)
        password: str (required)

    Return:
        status: str (success or failed)
        message: str (error message)
    
    Return example:
        {
            "status": "success"
        }
    
    Raises:
        ValidationError: if username or email or password is invalid
        Exception: if username or email is already existed

    Permission:
        AllowAny
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer

    # TODO: add email verification, password plaintext to hash
    def post(self, request, *args, **kwargs):
        try:
            serializer = UserRegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failed', 'message': serializer.errors})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserLoginView(generics.GenericAPIView):
    """
    User login view
    
    Prameters:
        username: str (required)
        password: str (required)

    Return:
        status: str (success or failed)
        message: str (error message)
        access_token: str (JWT access token)
        refresh_token: str (JWT refresh token)
        user_info: dict (user profile)
    
    Permission:
        AllowAny
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserProfileSerializer

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.is_active:
                    return JsonResponse({'status': 'failed', 'message': 'user is banned'})
                login(request, user)
                refresh_token = RefreshToken.for_user(user)
                access_token = str(refresh_token.access_token)
                refresh_token = str(refresh_token)
                serializers = UserProfileSerializer(user)
                user_info = serializers.data
                return JsonResponse({'status': 'success', 'access_token': access_token, 'refresh_token': refresh_token,
                                     'user_info': user_info})
            else:
                return JsonResponse({'status': 'failed', 'message': 'wrong username or password'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserReLoginView(generics.GenericAPIView):
    """
    User relogin view
    
    Prameters:
        refresh_token: str (required) (JWT refresh token)
    
    Return:
        status: str (success or failed)
        message: str (error message)
        access_token: str (JWT access token)
        refresh_token: str (JWT refresh token)
        user_info: dict (user profile)
    """

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh_token')
            refresh_token = RefreshToken(refresh_token)
            user = User.objects.get(userID=refresh_token['userID'])
            if user is not None:
                if not user.is_active:
                    return JsonResponse({'status': 'failed', 'message': 'user is banned'})
                login(request, user)
                refresh_token = RefreshToken.for_user(user)
                access_token = str(refresh_token.access_token)
                refresh_token = str(refresh_token)
                serializers = UserProfileSerializer(user)
                user_info = serializers.data
                return JsonResponse({'status': 'success', 'access_token': access_token, 'refresh_token': refresh_token,
                                     'user_info': user_info})
            else:
                return JsonResponse({'status': 'failed', 'message': 'wrong refresh token'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserLogoutView(generics.GenericAPIView):
    """
    User logout view

    Prameters:
        None

    Return:
        status: str (success or failed)
        message: str (error message)
    
    Permission:
        IsAuthenticated
    """
    def post(self, request, *args, **kwargs):
        try:
            logout(request)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserProfileView(generics.GenericAPIView):
    """
    User profile view

    Prameters:
        pk: int (required) (0 for current user)
    """
    permission_classes = [UserProfilePermission]
    serializer_class = UserProfileSerializer

    def get_object(self):
        if self.kwargs['pk'] == 0:
            return self.request.user
        return User.objects.get(userID=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        """
        basic info get

        Return:
            status: str (success or failed)
            user_info: dict (user profile)
        """
        try:
            user_info = UserProfileSerializer(self.get_object()).data
            return JsonResponse({'status': 'success', 'user_info': user_info})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})

    def post(self, request, *args, **kwargs):
        """
        basic info update for admin

        Prameters:
            password: str
            is_active: bool
            sex: str
            avatar: file
            status: str
            stuID: str
            college: str
            major: str
            birth_date: str
            address: str
            phone: str
            groups: list

        Return:
            status: str (success or failed)
            user_info: dict (user profile)
            message: str (error message)
        """
        try:
            queryset = self.get_object()
            serializer = UserProfileSerializer(queryset, request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(queryset, serializer.validated_data)
            if 'password' in request.data:
                queryset.set_password(request.data['password'])
                queryset.save()
            user_info = serializer.data
            return JsonResponse({'status': 'success', 'user_info': user_info})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})

    def patch(self, request, *args, **kwargs):
        """
        basic info update for user

        Prameters:
            sex: str
            avatar: file
            status: str
            stuID: str
            college: str
            major: str
            birth_date: str
            address: str
            phone: str
        
        Return:
            status: str (success or failed)
            user_info: dict (user profile)
            message: str (error message)
        """
        try:
            queryset = self.get_object()
            read_only_fields = ('groups', 'is_active')
            for item in read_only_fields:
                if item in request.data:
                    raise Exception('read only field cannot be changed')
            serializer = UserProfileSerializer(queryset, request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(queryset, serializer.validated_data)
            user_info = serializer.data
            return JsonResponse({'status': 'success', 'user_info': user_info})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})

    def delete(self, request, *args, **kwargs):
        """
        user delete

        Prameters:
            None

        Return:
            status: str (success or failed)
            message: str (error message)
        """
        try:
            self.get_object().delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserListView(generics.ListAPIView):
    """
    User list view
    
    Prameters:
        page_size: int (optional) (default: 10)
        page: int (optional) (default: 1)

    Return:
        pageinated_response: dict (user profile list)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = UserProfileSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            else:
                raise Exception('page is None')
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserPasswordChangeView(generics.GenericAPIView):
    """
    User password change view
    
    Prameters:
        old_password: str (required)
        new_password: str (required)
        
    Return:
        status: str (success or failed)
        message: str (error message)
    """
    def post(self, request, *args, **kwargs):
        try:
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')
            user = authenticate(request, username=request.user.username, password=old_password)
            if user is not None:
                user.set_password(new_password)
                user.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failed', 'message': 'wrong password'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserAvatarView(generics.GenericAPIView):
    """
    User avatar view

    Prameters:
        pk: int (required) (0 for current user)
    """
    permission_classes = [UserAvatarPermission]
    serializer_class = UserAvatarSerializer

    def get_object(self):
        if self.kwargs['pk'] == 0:
            return self.request.user
        return User.objects.get(userID=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        """
        avatar get
        
        Return:
            status: str (success or failed)
            user_info: dict (userID, avatar)
            message: str (error message)
        """
        try:
            user_info = UserAvatarSerializer(self.get_object()).data
            return JsonResponse({'status': 'success', 'user_info': user_info})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})

    def post(self, request, *args, **kwargs):
        """
        avatar update

        Prameters:
            avatar: file (required)

        Return:
            status: str (success or failed)
            user_info: dict (userID, avatar)
            message: str (error message)
        """
        try:
            tmpUser = self.get_object()
            serializer = self.serializer_class(tmpUser, request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            tmpUser.avatar.delete()
            serializer.update(tmpUser, serializer.validated_data)
            user_info = serializer.data
            return JsonResponse({'status': 'success', 'user_info': user_info})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})

    def delete(self, request, *args, **kwargs):
        """
        avatar delete
        
        Return:
            status: str (success or failed)
            message: str (error message)
        """
        try:
            tmpUser = self.get_object()
            tmpUser.avatar.delete()
            tmpUser.save()
            return JsonResponse({'status': 'success', 'message': 'avatar deleted'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})
