from rest_framework import serializers

from social_media.models import Profile, Post, Like, Comment, Follow


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "username",
            "first_name",
            "last_name",
            "bio",
            "pronouns",
            "avatar",
        )
        read_only_fields = ("user",)


class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False)

    class Meta:
        model = Post
        fields = ("id", "user", "content", "media_content", "posted", "hashtag")
        read_only_fields = ("user",)


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("id", "follower", "followed")


class LikeSerializer(serializers.ModelSerializer):
    post = PostSerializer(many=False)

    class Meta:
        model = Like
        fields = ("id", "post")


class LikePostSerializer(serializers.ModelSerializer):
    liked_by = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Like
        fields = ("id", "liked_by")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user", "post", "content")
        read_only_fields = ("user", "post")


class CommentPostSerializer(serializers.ModelSerializer):
    post = serializers.StringRelatedField(many=False)
    post_content = serializers.CharField(source="post.content", read_only=True)
    commented_by = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "post_content", "content", "commented_by")
