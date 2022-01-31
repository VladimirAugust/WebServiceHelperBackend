from django.contrib import admin
from .models import User, RegistrationLinkGenerator


admin.site.register(User)
admin.site.register(RegistrationLinkGenerator)
