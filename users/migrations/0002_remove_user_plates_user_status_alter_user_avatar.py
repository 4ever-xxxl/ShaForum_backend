# Generated by Django 4.2.6 on 2023-10-22 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="user", name="plates",),
        migrations.AddField(
            model_name="user",
            name="status",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="个性签名"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True, null=True, upload_to="media/avatars/", verbose_name="头像"
            ),
        ),
    ]
