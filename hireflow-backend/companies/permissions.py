from rest_framework.permissions import BasePermission


class IsCompany(BasePermission):
    message = "This endpoint is only available to companies."

    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, "auth_role", None) == "company")


class IsApprovedCompany(IsCompany):
    message = "Your company registration is still pending officer approval."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.status == "approved"
