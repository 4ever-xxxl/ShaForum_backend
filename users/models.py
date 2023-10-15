from django.db import models
from django.contrib.auth.models import Group, AbstractUser


class User(AbstractUser):
    """
    User model based on django.contrib.auth.models.User
    """
    userID = models.AutoField(primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=20, unique=True, verbose_name='用户名')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    stuID = models.CharField(max_length=20, null=True, blank=True, verbose_name='学号')
    college = models.CharField(max_length=100, null=True, blank=True, verbose_name='学院')
    major = models.CharField(max_length=100, null=True, blank=True, verbose_name='专业')
    birth_date = models.DateField(null=True, blank=True, verbose_name='生日')
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name='地址')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='电话')

    plates = models.ManyToManyField('posts.Plate', through='posts.ManagePlate', verbose_name='管理板块')

    class Meta:
        ordering = ['userID']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not Group.objects.filter(name='uestcer').exists():
            Group.objects.create(name='uestcer')
        group = Group.objects.get(name='uestcer')
        self.groups.add(group)


