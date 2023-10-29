from django.conf.urls.static import static
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView, TokenVerifyView

import settings
from . import views

app_name = 'users'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/balcklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    # 以上是simplejwt的自带路由

    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("profile/<int:pk>/", views.UserProfileView.as_view(), name="profile"),
    path("user/list/", views.UserListView.as_view(), name="userlist"),
    path("user/avatar/<int:pk>/", views.UserAvatarView.as_view(), name="avatar"),
    path("password/change/", views.UserPasswordChangeView.as_view(), name="password_change"),
]

