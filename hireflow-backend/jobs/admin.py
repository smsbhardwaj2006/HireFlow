from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "location", "salary", "job_type", "deadline"]
    list_filter = ["job_type", "company"]
    search_fields = ["title", "company__name"]
