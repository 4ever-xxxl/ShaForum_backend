from django.contrib import admin

from posts.models import Post, Plate, ManagePlate

# Register your models here.
admin.site.register(Post)
admin.site.register(Plate)
admin.site.register(ManagePlate)