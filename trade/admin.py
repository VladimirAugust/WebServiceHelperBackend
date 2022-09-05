from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from .models import *


@admin.register(GoodCategory)
class GoodCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("sort_order", "full_name", "is_service")
    search_fields = ("name", "id__iexact")

    def full_name(self, obj):
        return str(obj)

    full_name.short_description = 'Название'
    full_name.admin_order_field = 'parent'

    # ordering = ['sort_order']


class UploadedImageInlineAdmin(admin.TabularInline):
    model = UploadedImage


@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "category", "updated_at")
    search_fields = ("name", "id__iexact")
    list_filter = ("category", )
    inlines = [UploadedImageInlineAdmin, ]


@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "good", "created_at")
    search_fields = ("id", "user__id", "user__tg_id")


