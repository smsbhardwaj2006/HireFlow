from django.contrib import admin
from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ["application", "date", "time", "venue", "status"]
    list_filter = ["status"]
