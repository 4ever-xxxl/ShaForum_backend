from django.conf.urls.static import static
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView, TokenVerifyView

from API import settings
from . import views

app_name = 'users'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/balcklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    # 以上是simplejwt的自带路由

    path('home/', views.HomeView.as_view(), name='home'),

    path('register/code/', views.RegisterVerifyCodeView.as_view(), name='verifycode for register'),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path('relogin/', views.UserReLoginView.as_view(), name='relogin'),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("profile/<int:pk>/", views.UserProfileView.as_view(), name="profile"),
    path("user/list/", views.UserListView.as_view(), name="userlist"),
    path("user/avatar/<int:pk>/", views.UserAvatarView.as_view(), name="avatar"),

    path("password/change/", views.UserPasswordChangeView.as_view(), name="password_change"),
    path("password/reset/code/", views.UserPasswordResetVerifyView.as_view(), name="password_reset_verify"),
    path("password/reset/", views.UserPasswordResetView.as_view(), name="password_reset"),

    path("notification/list/", views.NotificationListView.as_view(), name="notification_list"),
    path("notification/<int:pk>/", views.NotificationDetailView.as_view(), name="notification_detail"),
    path("notification/read/<int:pk>/", views.NotificationReadView.as_view(), name="notification_read"),
    path("notification/all/read/", views.NotificationAllReadView.as_view(), name="notification_allread"),
]

