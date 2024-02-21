import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


def profile_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    if isinstance(instance, Profile):
        filename = f"{slugify(instance.username)}-{uuid.uuid4()}{extension}"
    if isinstance(instance, Post):
        filename = f"{slugify(instance.user.username)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/profiles/", filename)


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    username = models.CharField(max_length=63, unique=True)
    first_name = models.CharField(max_length=63, null=True, blank=True)
    last_name = models.CharField(max_length=63, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    pronouns = models.CharField(max_length=53, null=True, blank=True)
    avatar = models.ImageField(null=True, upload_to=profile_image_file_path)

    def follow(self, profile_to_follow):
        """Create a follow relationship."""
        if profile_to_follow != self:
            Follow.objects.get_or_create(follower=self, followed=profile_to_follow)

    def unfollow(self, profile_to_unfollow):
        """Remove a follow relationship."""
        Follow.objects.filter(follower=self, followed=profile_to_unfollow).delete()

    def is_following(self, profile):
        """Check if the user is following another profile."""
        return self.following.filter(followed=profile).exists()

    def is_followed_by(self, profile):
        """Check if the user is followed by another profile."""
        return self.followers.filter(follower=profile).exists()

    def __str__(self):
        return self.username


class Post(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(null=True, blank=True)
    media_content = models.ImageField(null=True, upload_to=profile_image_file_path)
    posted = models.DateTimeField(auto_now_add=True)

    def like(self, profile):
        """Like a post"""
        Like.objects.get_or_create(user=profile, post=self)

    def unlike(self, profile):
        """Unlike a post"""
        Like.objects.filter(user=profile, post=self).delete()

    def is_liked(self, profile):
        """Check liked posts"""
        return self.likes.filter(user=profile).exists()

    def __str__(self):
        return f"Posted by {self.user.username}"


class Follow(models.Model):
    follower = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="following"
    )
    followed = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="followers"
    )

    class Meta:
        unique_together = ("follower", "followed")


class Like(models.Model):
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    class Meta:
        unique_together = ("user", "post")


class Comment(models.Model):
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    content = models.TextField()

