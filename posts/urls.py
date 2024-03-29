from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    path('', views.index, name='index'),
    path('post/list/', views.PostListView.as_view(), name='post_list'),  # 用于获取帖子列表

    path('post/hot/list/', views.PostHotListView.as_view(), name='post_hot_list'),  # 用于获取热门帖子列表
    path('post/essence/list/', views.PostEssenceListView.as_view(), name='post_essence_list'),  # 用于获取精华帖子列表

    path('post/create/', views.PostCreateView.as_view(), name='post_create'),  # 用于创建帖子
    path('post/detail/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),  # 用于获取帖子详情
    path('post/action/<int:pk>/', views.PostActionView.as_view(), name='post_action'),  # 对帖子进行操作
    path('post/like/<int:pk>/', views.PostLikeView.as_view(), name='post_like'),  # 对帖子进行点赞
    path('post/collect/<int:pk>/', views.PostCollectView.as_view(), name='post_collect'),  # 对帖子进行收藏
    path('post/coverImg/<int:pk>/', views.PostCoverImgView.as_view(), name='post_coverImg'),  # 对帖子进行封面图片操作
    path('post/comment/<int:pk>/', views.PostCommentView.as_view(), name='post_comment'),  # 对帖子进行评论
    path('post/comment/list/<int:pk>/', views.PostCommentListView.as_view(), name='post_comment_list'),  # 获取帖子评论列表
    path('post/status/<int:pk>/', views.PostStatusView.as_view(), name='post_status'),  # 获取帖子状态


    path('post/my/list/', views.MyPostListView.as_view(), name='my_post_list'),  # 获取我的帖子列表
    # path('post/my/like/list/', views.MyPostLikeListView.as_view(), name='my_post_like_list'),  # 获取我的点赞帖子列表
    # path('post/my/collect/list/', views.MyPostCollectListView.as_view(), name='my_post_collect_list'),  # 获取我的收藏帖子列表
    # path('post/my/comment/list/', views.MyPostCommentListView.as_view(), name='my_post_comment_list'),  # 获取我的评论帖子列表


    path('plate/list/', views.PlateListView.as_view(), name='plate_list'),  # 用于获取板块列表
    path('plate/<int:pk>/', views.PlateDetailView.as_view(), name='plate_detail'),  # 用于获取板块详情
    path('plate/create/', views.PlateCreateView.as_view(), name='plate_create'),  # 用于创建板块
    path('plate/action/<int:pk>/', views.PlateActionView.as_view(), name='plate_action'),  # 对板块进行操作
    path('plate/manage/list/', views.ManagePlateListView.as_view(), name='ManagePlateListView'),  # 用于获取管理板块列表
    path('plate/manage/create/', views.ManagePlateCreateView.as_view(), name='ManagePlateCreateView'),  # 用于任命版主
    path('plate/manage/<int:pk>/', views.ManagePlateActionView.as_view(), name='plate_manage'),  # 对板块进行管理

]