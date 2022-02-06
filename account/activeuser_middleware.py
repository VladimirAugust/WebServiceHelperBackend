import datetime
from django.core.cache import cache
from django.conf import settings
from rest_framework.authtoken.models import Token

from .services.user_services import get_user_by_request
from django.utils.deprecation import MiddlewareMixin


class ActiveUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            current_user = get_user_by_request(request)
        except Token.DoesNotExist:
            return
        if current_user:
            now = datetime.datetime.now()
            cache.set('seen_%s' % current_user.username, now,
                      settings.USER_LASTSEEN_TIMEOUT)

