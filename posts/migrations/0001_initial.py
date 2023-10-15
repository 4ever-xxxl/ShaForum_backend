# Generated by Django 4.2.6 on 2023-10-15 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ManagePlate",
            fields=[
                (
                    "mpID",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="管理板块ID"
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="任命时间"),
                ),
            ],
            options={"ordering": ("-created",),},
        ),
        migrations.CreateModel(
            name="Plate",
            fields=[
                (
                    "plateID",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="板块ID"
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="板块名")),
                ("description", models.TextField(verbose_name="板块描述")),
            ],
            options={"ordering": ("plateID",),},
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "postID",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="帖子ID"
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="标题")),
                ("content", models.TextField(verbose_name="内容")),
                (
                    "coverImg",
                    models.ImageField(
                        blank=True, null=True, upload_to="covers/", verbose_name="封面"
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "last_modified",
                    models.DateTimeField(auto_now=True, verbose_name="最后修改时间"),
                ),
                ("is_essence", models.BooleanField(default=False, verbose_name="是否加精")),
            ],
            options={"ordering": ("-created",),},
        ),
    ]
