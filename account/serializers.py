from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .services.user_services import get_user_by_request


User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    is_current_user = serializers.SerializerMethodField("is_current_session_user")
    is_online = serializers.SerializerMethodField("is_user_online")

    class Meta:
        model = User
        fields = ("username", "avatar", "description", "is_current_user", "is_online")

    def is_user_online(self, obj):
        return obj.is_online()

    def is_current_session_user(self, obj):
        """Check if current session user equals input user"""
        try:
            current_session_user = get_user_by_request(self.context.get("request"))
        except Token.DoesNotExist:
            return False
        if obj:
            if current_session_user == obj:
                return True
        return False


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


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )
        email = email.lower()
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        try:
            user = User.objects.get(email=email, password=password)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Пользователь с такой почтой или паролем не найден'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'Пользователь был деактивирован'
            )

        token = Token.objects.get(user=user)

        return {
            'email': user.email,
            'username': user.username,
            'token': token
        }
