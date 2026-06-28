from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Officer


@admin.register(Officer)
class OfficerAdmin(UserAdmin):
    model = Officer
    list_display = ["email", "name", "is_staff", "date_joined"]
    search_fields = ["email", "name"]
    ordering = ["-date_joined"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "name", "password1", "password2")}),
    )
