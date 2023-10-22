from mptt.models import MPTTModel, TreeForeignKey
from users.models import User
from posts.models import Post
from django.db import models


class Comment(MPTTModel):
    """
    Comment model
    """
    commentID = models.AutoField(primary_key=True, verbose_name='评论ID')
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", verbose_name='作者')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name='帖子')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='childComments',
                            verbose_name='父评论')
    reply_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='replies',
                                 verbose_name='回复给')

    # 以下字段已在外键中定义
    # childComments = models.ManyToManyField('comments.Comment', through='comments.models.Comment', verbose_name='子评论')

    # 以下字段已在关联模型中定义
    # whoLikes = models.ManyToManyField(User, through='models.models.py', verbose_name='点赞用户')
    # whoCollects = models.ManyToManyField(User, through='models.CollectUserComment', verbose_name='收藏用户')

    class MPTTMeta:
        order_insertion_by = ['created']

    def __str__(self):
        return self.content[10:]


class LikeUserComment(models.Model):
    """
    LikeUserComment model
    """
    likeUserCommentID = models.AutoField(primary_key=True, verbose_name='点赞评论ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likeComments", verbose_name='用户')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="whoLikes",verbose_name='评论')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.user.username + ' likes ' + self.comment.content[10:]


class CollectUserComment(models.Model):
    """
    CollectUserComment model
    """
    collectUserCommentID = models.AutoField(primary_key=True, verbose_name='收藏评论ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collectComments", verbose_name='用户')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="whoCollects", verbose_name='评论')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.user.username + ' collects ' + self.comment.content[10:]