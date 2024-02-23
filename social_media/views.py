from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Profile, Post
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import ProfileSerializer, PostSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        return Response(serializer.data)

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def following(self, request, pk=None):
        """Endpoint for retrieving all users that the user is following."""
        profile = self.get_object()
        all_followings = profile.all_followings()
        serializer = ProfileSerializer(all_followings, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly,)

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

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
