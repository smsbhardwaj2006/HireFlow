from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "status", "date_joined"]
    list_filter = ["status"]
    search_fields = ["name", "email"]
    exclude = ["password"]
