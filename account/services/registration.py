from account.models import RegistrationLinkGenerator, User
from account.exceptions import UserAlreadyExist, URLHashDoesNotExist
from typing import Union
from rest_framework.authtoken.models import Token


def is_link_valid(url_hash: str) -> Union[bool, RegistrationLinkGenerator]:
    try:
        register_link = RegistrationLinkGenerator.objects.get(url_hash=url_hash)

    except RegistrationLinkGenerator.DoesNotExist:
        return False

    if not register_link.is_alive:
        register_link.delete()
        return False

    return register_link


def create_user(username: str, email: str, password: str, url_hash: str) -> str:
    link = is_link_valid(url_hash)
    if not link:
        raise URLHashDoesNotExist()

    user, created = User.objects.get_or_create(username=username,
                                               email=email,
                                               password=password)
    if created:
        user.save()
        token = Token.objects.create(user=user)
        link.delete()
        return token.key
    else:
        raise UserAlreadyExist()
