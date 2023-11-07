from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from users.permissions import UserProfilePermission, UserAvatarPermission
from users.serializers import UserRegisterSerializer, UserProfileSerializer, UserAvatarSerializer, NotificationSerializer
from users.models import User
from API.CustomPagination import CustomPagination
from django.core.mail import send_mail
from django.core.cache import cache
from datetime import datetime, timedelta
from API.settings import DEFAULT_FROM_EMAIL
import logging

logger = logging.getLogger('django')

class RegisterVerificationCodeView(generics.GenericAPIView):
    """
    Send verification code view
    
    Prameters:
        email: str (required)

    Return:
        status: str (success or failed)
        message: str (error message)
    
    Return example:
        {
            "status": "success"
        }
    
    Raises:
        ValidationError: if email is invalid
        Exception: if email is already existed

    Permission:
        AllowAny
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'failed', 'message': 'email already exists'})
            
            cache_key = 'verify_code_{}'.format(request.session.session_key)
            cache_key_time = 'verify_code_time_{}'.format(request.session.session_key)
            
            last_sent = cache.get(cache_key_time)
            if last_sent and datetime.now() - last_sent < timedelta(seconds=60):
                return JsonResponse({'status': 'failed', 'message': 'Please wait for a while before requesting again.'})
            
            # 生成验证码
            verify_code = User.objects.make_random_password(length=6, allowed_chars='1234567890')

            send_mail(
                subject='ShaForum 注册验证码',
                message="""
                您的验证码为：{verify_code}
                请在5分钟内完成注册。
                请勿回复本邮件。
                """.format(verify_code=verify_code),
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            cache.set(cache_key, verify_code, timeout=300)
            cache.set(cache_key_time, datetime.now(), timeout=60)
            return JsonResponse({'status': 'success', 'message': 'verification code sent, expires in 5 minutes'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})

class UserRegisterView(generics.CreateAPIView):
    """
    User register view
    
    Prameters:
        username: str (required)
        email: str (required)
        password: str (required)
        code: str (required)

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

    def post(self, request, *args, **kwargs):
        try:
            cache_key = 'verify_code_{}'.format(request.session.session_key)
            verify_code = cache.get(cache_key)
            if verify_code is None:
                return JsonResponse({'status': 'failed', 'message': 'verification code expired'})
            elif verify_code != request.data.get('code'):
                return JsonResponse({'status': 'failed', 'message': 'wrong verification code'})
            cache.delete(cache_key)
            
            serializer = UserRegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                del request.session['verify_code']
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
                expired_time = refresh_token['exp']
                refresh_token = str(refresh_token)
                serializers = UserProfileSerializer(user, context={'request': request})
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
    permission_classes = [permissions.AllowAny]
    serializer_class = UserProfileSerializer

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
                serializers = self.serializer_class(user)
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
            user_info = self.serializer_class(self.get_object(), context={'request': request}).data
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
            serializer = self.serializer_class(queryset, request.data, partial=True, context={'request': request})
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
            serializer = self.serializer_class(queryset, request.data, partial=True, context={'request': request})
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
                serializer = UserProfileSerializer(page, many=True, context={'request': request})
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
            user_info = UserAvatarSerializer(self.get_object(), context={'request': request}).data
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
            serializer = self.serializer_class(tmpUser, request.data, partial=True, context={'request': request})
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


class NotificationListView(generics.ListAPIView):
    """
    Notification list view
    
    Prameters:
        page_size: int (optional) (default: 10)
        page: int (optional) (default: 1)

    Return:
        pageinated_response: dict (notification list)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.request.user.notifications.all()

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = NotificationSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            else:
                raise Exception('page is None')
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class NotificationDetailView(generics.GenericAPIView):
    """
    Notification detail view
    
    Prameters:
        pk: int (required) (notification id)
    
    Return:
        status: str (success or failed)
        notification_info: dict (notification detail)
        message: str (error message)
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_object(self):
        return self.request.user.notifications.get(id=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        try:
            notification = self.get_object(raise_exception=True)
            notification_info = NotificationSerializer(notification).data
            return JsonResponse({'status': 'success', 'notification_info': notification_info})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})
        

class NotificationReadView(generics.GenericAPIView):
    """
    Notification read/unread view
    
    Prameters:
        pk: int (required) (notification id)
        
    Return:
        status: str (success or failed)
        message: str (error message)
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_object(self):
        return self.request.user.notifications.get(id=self.kwargs['pk'])
    
    def post(self, request, *args, **kwargs):
        try:
            notification = self.get_object(raise_exception=True)
            notification.mark_as_read()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})
        
    def delete(self, request, *args, **kwargs):
        try:
            notification = self.get_object(raise_exception=True)
            notification.mark_as_unread()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})
        

class NotificationAllReadView(generics.GenericAPIView):
    """
    Notification all read view
    
    Prameters:
        None
        
    Return:
        status: str (success or failed)
        message: str (error message)
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            request.user.notifications.mark_all_as_read()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})
        
    def delete(self, request, *args, **kwargs):
        try:
            request.user.notifications.mark_all_as_unread()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})
