from abc import ABC

from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "avatar", "description", "abilities")


class RegisterPageSerializer(serializers.Serializer):
    url_hash = serializers.CharField(max_length=64, required=True)

    def validate(self, data):
        return {
            "url_hash": data["url_hash"]
        }


class RegisterUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    url_hash = serializers.CharField(max_length=64, required=True)

    def validate(self, data):
        return {
            "email": data["email"],
            "password": data["password"],
            "username": data["username"],
            "url_hash": data["url_hash"]
        }
