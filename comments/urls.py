from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path('comment/list/', views.CommentListView.as_view(), name='comment_list'),  # 用于获取评论列表
    path('comment/create/', views.CommentCreateView.as_view(), name='comment_create'),  # 用于创建评论
    path('comment/detail/<int:pk>/', views.CommentDetailView.as_view(), name='comment_detail'),  # 用于获取评论详情
    path('comment/action/<int:pk>/', views.CommentActionView.as_view(), name='comment_action'),  # 对评论进行操作
    path('comment/like/<int:pk>/', views.CommentLikeView.as_view(), name='comment_like'),  # 对评论进行点赞
    path('comment/collect/<int:pk>/', views.CommentCollectView.as_view(), name='comment_collect'),  # 对评论进行收藏
    # path('comment/reply/<int:pk>/', views.CommentReplyView.as_view(), name='comment_reply'),  # 对评论进行回复
]