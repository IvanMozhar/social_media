from django.contrib import admin

from social_media.models import (
    Profile,
    Post,
    Like,
    Comment,
    Follow
)

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follow)
