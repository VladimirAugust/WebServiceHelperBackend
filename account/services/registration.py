from account.models import User
from account.exceptions import UserAlreadyExist
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string





def generate_confirm_code():
    return get_random_string(length=5, allowed_chars='1234567890')


def create_user(username: str, email: str, password: str,) -> str:
    user, created = User.objects.get_or_create(username=username,
                                               email=email)
    if created:
        user.set_password(password)
        user.save()
        token = Token.objects.create(user=user)
        return token.key
    else:
        raise UserAlreadyExist()
