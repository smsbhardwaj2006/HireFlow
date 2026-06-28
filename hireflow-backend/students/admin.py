from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "branch", "cgpa", "profile_completion", "date_joined"]
    list_filter = ["branch", "course"]
    search_fields = ["name", "email"]
    exclude = ["password"]  # never show the hash in the admin form
