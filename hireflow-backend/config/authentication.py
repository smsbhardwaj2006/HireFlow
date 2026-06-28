"""
Custom multi-role JWT authentication.

Why this file exists: Django REST Framework's permission classes
(IsAuthenticated, etc.) and SimpleJWT's default authentication both assume
exactly one user model (AUTH_USER_MODEL). We have three — Student, Company,
Officer — none of which is "the" user model, by design (see the models.py
docstrings in each app for why).

The fix: every JWT we issue carries a custom claim, "role" ("student",
"company", or "officer"), set at login time (see each app's views.py).
This authentication class reads that claim and looks the user up in the
matching table instead of always querying AUTH_USER_MODEL. Once resolved,
request.user is a real Student/Company/Officer instance, and
request.auth_role tells every view which kind of user it's looking at —
that's what view-level permission classes (IsStudent, IsCompany, IsOfficer
in each app's permissions.py) check.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class MultiRoleJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        role = validated_token.get("role")
        user_id = validated_token.get("user_id")

        if role == "student":
            from students.models import Student
            model = Student
        elif role == "company":
            from companies.models import Company
            model = Company
        elif role == "officer":
            from officers.models import Officer
            model = Officer
        else:
            raise AuthenticationFailed("Token is missing a valid role claim.")

        try:
            user = model.objects.get(id=user_id)
        except model.DoesNotExist:
            raise AuthenticationFailed(f"No {role} found for this token.")

        # Tag the resolved instance with its role so permission classes
        # (IsStudent / IsCompany / IsOfficer) can check it without having
        # to re-derive it from the object's type.
        user.auth_role = role
        return user
