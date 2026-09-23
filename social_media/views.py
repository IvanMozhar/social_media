from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Profile, Post, Like, Comment
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import (
    ProfileSerializer,
    PostSerializer,
    LikeSerializer,
    CommentSerializer,
    CommentPostSerializer,
    LikePostSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        if Profile.objects.filter(user=self.request.user).exists():
            raise ValidationError("You already have a profile.")
        serializer.save(user=self.request.user)

    def get_queryset(self):
        username = self.request.query_params.get("username")
        bio = self.request.query_params.get("bio")

        queryset = self.queryset

        if username:
            queryset = queryset.filter(username__icontains=username)

        if bio:
            queryset = queryset.filter(bio__icontains=bio)

        return queryset.distinct()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsOwnerOrReadOnly],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """Endpoint for following another user."""
        if request.user.profile.pk == int(pk):
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_to_follow = get_object_or_404(Profile, pk=pk)
        if request.user.profile.is_following(user_to_follow):
            return Response(
                {"detail": "You are already following this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.profile.follow(user_to_follow)
        return Response(
            {"detail": "You are now following this user"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        """Endpoint for unfollowing another user."""
        if request.user.profile.pk == int(pk):
            return Response(
                {"detail": "You cannot unfollow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_to_unfollow = get_object_or_404(Profile, pk=pk)
        if not request.user.profile.is_following(user_to_unfollow):
            return Response(
                {"detail": "You are not following this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.profile.unfollow(user_to_unfollow)
        return Response(
            {"detail": "Unfollowed successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def followers(self, request, pk=None):
        """Endpoint for retrieving all followers of a user."""
        profile = self.get_object()
        all_followers = profile.all_followers()

        serializer = ProfileSerializer(all_followers, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def following(self, request, pk=None):
        """Endpoint for retrieving all users that the user is following."""
        profile = self.get_object()
        all_followings = profile.all_followings()
        serializer = ProfileSerializer(all_followings, many=True)
        return Response(serializer.data)

    @action(methods=["GET"], detail=True, permission_classes=[IsAuthenticated])
    def all_likes(self, request, pk=None):
        """Endpoint for viewing all liked posts"""
        profile = self.get_object()
        all_likes = profile.all_likes()
        serializer = LikeSerializer(all_likes, many=True)
        if profile == request.user.profile:
            return Response(serializer.data)
        return Response(
            {"detail": "You cannot see posts liked by other user"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Filter profiles by username (ex. ?username=adm)",
            ),
            OpenApiParameter(
                "bio",
                type=OpenApiTypes.STR,
                description="Filter profiles by bio (ex. ?bio=am)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List of profiles with filter by bio and username"""
        return super().list(request, *args, **kwargs)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("user")
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        hashtag = self.request.query_params.get("hashtag")
        content = self.request.query_params.get("content")
        username = self.request.query_params.get("username")

        queryset = self.queryset

        if hashtag:
            queryset = queryset.filter(hashtag__icontains=hashtag)

        if content:
            queryset = queryset.filter(content__icontains=content)

        if username:
            queryset = queryset.filter(likes__user__username=username)

        return queryset.distinct()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsOwnerOrReadOnly],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to post"""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Endpoint for liking a post."""
        post = get_object_or_404(Post, pk=pk)
        liked = Like.objects.filter(user=request.user.profile, post=post).exists()

        if liked:
            return Response(
                {"detail": "You have already liked this post"},
                status=status.HTTP_200_OK,
            )
        post.like(request.user.profile)
        return Response({"detail": "You liked this post"}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        """Endpoint for unliking a post."""
        post = get_object_or_404(Post, pk=pk)
        liked = Like.objects.filter(user=request.user.profile, post=post).exists()
        if not liked:
            return Response(
                {"detail": "You have not liked this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        post.unlike(request.user.profile)
        return Response(
            {"detail": "You unliked this post"},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAuthenticated],
        serializer_class=CommentSerializer,
    )
    def add_comment(self, request, pk=None):
        """Endpoint for adding a comment"""
        post = get_object_or_404(Post, pk=pk)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user.profile, post=post)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        """Endpoints to list all comments"""
        post = self.get_object()
        comments = (
            Comment.objects.filter(post=post)
            .select_related("post", "user")
            .prefetch_related("post__user")
        )
        serializer = CommentPostSerializer(comments, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def likes(self, request, pk=None):
        """Endpoints to list all likes on the post"""
        post = self.get_object()
        likes = (
            Like.objects.filter(post=post)
            .select_related("post", "user")
            .prefetch_related("post__user")
        )
        serializer = LikePostSerializer(likes, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["GET", "PUT", "DELETE"],
        permission_classes=[IsAuthenticated],
        serializer_class=CommentSerializer,
        url_path="comments/(?P<comment_pk>[^/.]+)/edit",
    )
    def edit_comment(self, request, pk=None, comment_pk=None):
        """Endpoint for editing comment (users can only edit their own comments)"""
        comment = get_object_or_404(Comment, pk=comment_pk, post__id=pk)

        self.check_object_permissions(request, comment)

        if request.method == "GET":
            serializer = CommentSerializer(comment)
            return Response(serializer.data)

        elif request.method == "PUT":
            if request.user.profile != comment.user:
                return Response(
                    {"detail": "You do not have permission to edit this comment."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = CommentSerializer(comment, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == "DELETE":
            if request.user != comment.user:
                return Response(
                    {"detail": "You do not have permission to delete this comment."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Filter posts by username (ex. ?username=adm)",
            ),
            OpenApiParameter(
                "content",
                type=OpenApiTypes.STR,
                description="Filter posts by content (ex. ?content=This)",
            ),
            OpenApiParameter(
                "hashtag",
                type=OpenApiTypes.STR,
                description="Filter posts by hashtag (ex. ?hashtag=This)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List of posts with filter by hashtag, content and username"""
        return super().list(request, *args, **kwargs)
