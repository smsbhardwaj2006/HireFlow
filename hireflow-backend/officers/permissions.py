from rest_framework.permissions import BasePermission


class IsOfficer(BasePermission):
    message = "This endpoint is only available to placement officers."

    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, "auth_role", None) == "officer")
