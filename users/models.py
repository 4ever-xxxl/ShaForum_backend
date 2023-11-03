from django.db import models
from django.contrib.auth.models import Group, AbstractUser


class User(AbstractUser):
    """
    User model based on django.contrib.auth.models.User
    """
    userID = models.AutoField(primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=20, unique=True, verbose_name='用户名')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    sex = models.CharField(max_length=10, null=True, blank=True, verbose_name='性别')
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True, verbose_name='头像')
    stuID = models.CharField(max_length=20, null=True, blank=True, verbose_name='学号')
    college = models.CharField(max_length=100, null=True, blank=True, verbose_name='学院')
    major = models.CharField(max_length=100, null=True, blank=True, verbose_name='专业')
    birth_date = models.DateField(null=True, blank=True, verbose_name='生日')
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name='地址')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='电话')
    status = models.CharField(max_length=50, null=True, blank=True, verbose_name='个性签名')

    # 以下字段已在外键中定义、
    # posts = models.ManyToManyField('posts.Post', through='posts.models.Post', verbose_name='帖子')
    # comments = models.ManyToManyField('comments.Comment', through='comments.models.Comment', verbose_name='评论')

    # 以下字段已在关联模型中定义
    # likePosts = models.ManyToManyField('posts.Post', through='posts.models.LikeUserPost', verbose_name='点赞帖子')
    # collectPosts = models.ManyToManyField('posts.Post', through='posts.models.CollectUserPost', verbose_name='收藏帖子')
    # likeComments = models.ManyToManyField('comments.Comment', through='comments.models.LikeUserComment', verbose_name='点赞评论')
    # collectComments = models.ManyToManyField('comments.Comment', through='comments.models.CollectUserComment', verbose_name='收藏评论')
    # managePlates = models.ManyToManyField('posts.Plate', through='posts.ManagePlate', verbose_name='管理板块')
    # replys = models.ManyToManyField('comments.Comment', through='comments.models.Reply', verbose_name='被回复')

    class Meta:
        ordering = ['userID']

    def __str__(self):
        return self.username

    # 重写save方法，创建用户时自动加入uestcer组
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not Group.objects.filter(name='uestcer').exists():
            Group.objects.create(name='uestcer')
        group = Group.objects.get(name='uestcer')
        self.groups.add(group)


