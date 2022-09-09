from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from .serializers import (RegisterUserSerializer, UserChangeAvatarSerializer, LoginSerializer, \
                          UserSettingsSerializer, ProfileSerializer, UserPasswordChangeSerializer, UserInfoSerializer, \
                          BlockUserSerializer)
from django.contrib.auth import get_user_model


User = get_user_model()


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class BlockUserAPIView(generics.UpdateAPIView):
    model = User
    permission_classes = (IsModerator,)
    serializer_class = BlockUserSerializer

    def get_object(self, queryset=None):
        instance = get_object_or_404(User, pk=self.request.data.get("pk", -1))
        if instance.is_superuser or instance.is_staff:
            raise ValidationError("Пользователь является модератором или админом")
        return instance


class UploadAvatarAPIView(generics.UpdateAPIView):
    model = User
    permission_classes = (IsAuthenticated,)
    serializer_class = UserChangeAvatarSerializer

    def get_object(self, queryset=None):
        return self.request.user


class APIChangePasswordView(generics.UpdateAPIView):
    serializer_class = UserPasswordChangeSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user


class SettingsAPIView(generics.UpdateAPIView):
    """
    Выставляет настройки юзера.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSettingsSerializer

    def post(self, request) -> Response:
        user = request.user
        serializer = self.serializer_class(data=request.data, context={"request": request}, instance=user)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"status": "ok"})

    def get(self, request) -> Response:
        serializer = self.serializer_class(request.user, context={"request": request})
        return Response(serializer.data) # TODO: test it, we removed status200


class LoginAPIView(APIView):
    """This view authenticate user. It returns token"""
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    """
    This view returns current user info:
    balance, avatar url, username, etc
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserInfoAPIView(APIView):
    """Возращает информацию о юзере."""
    permission_classes = (AllowAny,)
    serializer_class = UserInfoSerializer

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        serializer = self.serializer_class(user, context={
            "request": request
        })
        return Response(serializer.data)


class RegisterAPIView(APIView):
    """Регстрирует пользователя"""
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer

    def post(self, request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = dict(serializer.validated_data)
        if validated_data.get("code"): #    TODO: test it
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
