from django.urls import path, include
from . import views

app_name = 'posts'
urlpatterns = [
    path('', views.index, name='index'),
    path('postlist/', views.PostListView.as_view(), name='post_list'),  # 用于获取帖子列表
    path('post_detail/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),  # 用于获取帖子详情
    path('post_action/<int:pk>/', views.PostActionView.as_view(), name='post_action'),  # 对帖子进行操作
    path('post_action/', views.PostActionView.as_view(), name='poslistt_create'),  # 用于创建帖子
    # path('plate/', views.PlateListView.as_view(), name='plate_list'),
    # path('plate/<int:pk>/', views.PlateDetailView.as_view(), name='plate_detail'),

]