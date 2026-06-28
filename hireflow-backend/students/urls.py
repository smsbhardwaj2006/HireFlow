from django.urls import path
from .views import (
    StudentRegisterView, StudentLoginView, StudentProfileView, StudentResumeUploadView,
    AdminStudentListCreateView, AdminStudentDetailView,
)

urlpatterns = [
    path("students/register", StudentRegisterView.as_view(), name="student-register"),
    path("students/login", StudentLoginView.as_view(), name="student-login"),
    path("students/profile", StudentProfileView.as_view(), name="student-profile"),
    path("students/resume", StudentResumeUploadView.as_view(), name="student-resume"),

    # Officer-only management
    path("admin/students", AdminStudentListCreateView.as_view(), name="admin-student-list"),
    path("admin/students/<int:pk>", AdminStudentDetailView.as_view(), name="admin-student-detail"),
]
