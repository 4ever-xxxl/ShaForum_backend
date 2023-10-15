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

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            verbose_name='父评论')
    reply_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='replies',
                                 verbose_name='回复给')

    class MPTTMeta:
        order_insertion_by = ['created']

    def __str__(self):
        return self.content[10:]
