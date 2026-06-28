from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    message = "This endpoint is only available to students."

    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, "auth_role", None) == "student")
