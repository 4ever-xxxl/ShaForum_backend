# Generated by Django 4.2.6 on 2023-10-15 05:07

import django.contrib.auth.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("posts", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "userID",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="用户ID"
                    ),
                ),
                (
                    "username",
                    models.CharField(max_length=20, unique=True, verbose_name="用户名"),
                ),
                (
                    "email",
                    models.EmailField(max_length=254, unique=True, verbose_name="邮箱"),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True, null=True, upload_to="avatars/", verbose_name="头像"
                    ),
                ),
                (
                    "stuID",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="学号"
                    ),
                ),
                (
                    "college",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="学院"
                    ),
                ),
                (
                    "major",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="专业"
                    ),
                ),
                (
                    "birth_date",
                    models.DateField(blank=True, null=True, verbose_name="生日"),
                ),
                (
                    "address",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="地址"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="电话"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "plates",
                    models.ManyToManyField(
                        through="posts.ManagePlate",
                        to="posts.plate",
                        verbose_name="管理板块",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={"ordering": ["userID"],},
            managers=[("objects", django.contrib.auth.models.UserManager()),],
        ),
    ]
