from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


User = get_user_model()


def get_user_by_name(username: str) -> User:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise

    return User


def get_user_by_request(request) -> str:
    """Получает токен из header Authorization. Возращает юзера по токену"""
    header = get_authorization_header(request).decode("utf-8")
    if "Token" in header:
        token_key = header.replace("Token ", "")
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return False

        return token.user
