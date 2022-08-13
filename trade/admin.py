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

@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    pass
