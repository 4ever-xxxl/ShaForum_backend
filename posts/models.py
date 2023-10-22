from django.db import models
from markdown import Markdown
from taggit.managers import TaggableManager

from users.models import User


class Post(models.Model):
    """
    Post model
    """
    postID = models.AutoField(primary_key=True, verbose_name='帖子ID')
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", verbose_name='作者')
    coverImg = models.ImageField(upload_to='media/covers/', null=True, blank=True, verbose_name='封面')
    plate = models.ForeignKey('Plate', on_delete=models.CASCADE, related_name="posts", verbose_name='板块')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    is_essence = models.BooleanField(default=False, verbose_name='是否加精')
    tags = TaggableManager(blank=True, verbose_name='标签')
    views = models.PositiveIntegerField(default=0, verbose_name='浏览量')

    # 以下字段已在外键中定义
    # comments = models.ManyToManyField('comments.Comment', through='comments.models.Comment', verbose_name='评论')

    # 以下字段已在关联模型中定义
    # whoLikes = models.ManyToManyField(User, through='models.models.py', verbose_name='点赞用户')
    # whoCollects = models.ManyToManyField(User, through='models.CollectUserPost', verbose_name='收藏用户')
    # comments = models.ManyToManyField('comments.Comment', through='comments.models.Comment', verbose_name='评论')

    class Meta:
        ordering = ('-created',)

    def get_md(self):
        md = Markdown(
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
            ]
        )
        md_content = md.convert(self.content)
        # toc 是渲染后的目录
        return md_content, md.toc

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def __str__(self):
        return self.title


class Plate(models.Model):
    """
    Plate model
    """
    plateID = models.AutoField(primary_key=True, verbose_name='板块ID')
    name = models.CharField(max_length=100, verbose_name='板块名')
    description = models.TextField(verbose_name='板块描述')

    # 以下字段已在外键中定义
    # posts = models.ManyToManyField('posts.Post', through='posts.models.Post', verbose_name='帖子')

    # 以下字段已在关联模型中定义
    # moderators = models.ManyToManyField(User, through='ManagePlate', verbose_name='版主')

    class Meta:
        ordering = ('plateID',)

    def __str__(self):
        return self.name


class ManagePlate(models.Model):
    """
    ManagePlate model
    """
    mpID = models.AutoField(primary_key=True, verbose_name='管理板块ID')
    plate = models.ForeignKey(Plate, on_delete=models.CASCADE, related_name="moderators", verbose_name='板块')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="managePlates", verbose_name='版主')
    created = models.DateTimeField(auto_now_add=True, verbose_name='任命时间')

    class Meta:
        unique_together = ('plate', 'moderator')
        ordering = ('-created',)

    def __str__(self):
        return self.plate.name + ' ' + self.moderator.username


class LikeUserPost(models.Model):
    """
    Like model
    """
    likeID = models.AutoField(primary_key=True, verbose_name='点赞ID')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="whoLikes", verbose_name='帖子')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likePosts", verbose_name='用户')
    created = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    class Meta:
        unique_together = ('post', 'user')
        ordering = ('-created',)

    def __str__(self):
        return self.post.title + ' ' + self.user.username


class CollectUserPost(models.Model):
    """
    Collect model
    """
    collectID = models.AutoField(primary_key=True, verbose_name='收藏ID')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="whoCollects", verbose_name='帖子')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collectPosts", verbose_name='用户')
    created = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        unique_together = ('post', 'user')
        ordering = ('-created',)

    def __str__(self):
        return self.post.title + ' ' + self.user.username
