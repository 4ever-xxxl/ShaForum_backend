from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from users.permissions import UserProfilePermission
from users.serializers import UserRegisterSerializer, UserProfileSerializer
from users.models import User


class UserRegisterView(generics.CreateAPIView):
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


class UserLogoutView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        try:
            logout(request)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserProfileView(generics.GenericAPIView):
    permission_classes = [UserProfilePermission]
    serializer_class = UserProfileSerializer

    def get_object(self):
        if self.kwargs['pk'] == 0:
            return self.request.user
        return User.objects.get(userID=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        try:
            user_info = UserProfileSerializer(self.get_object()).data
            return JsonResponse({'status': 'success', 'user_info': user_info})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})

    def post(self, request, *args, **kwargs):
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
        try:
            self.get_object().delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = UserProfileSerializer(queryset, many=True)
            user_list = serializer.data
            return JsonResponse({'status': 'success', 'user_list': user_list})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})


class UserPasswordChangeView(generics.GenericAPIView):
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
