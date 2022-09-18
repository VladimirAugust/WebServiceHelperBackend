from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "tg_id", "first_name", "last_name", "city", "phone_number", "date_joined")
    search_fields = ("tg_id", "first_name", "phone_number")
