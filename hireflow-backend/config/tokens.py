"""
Issues JWT access/refresh tokens carrying a custom "role" claim, so
MultiRoleJWTAuthentication (see authentication.py) knows which table to
look the user up in later. Used by students/views.py, companies/views.py,
and officers/views.py — kept in one place so the three login endpoints
can't drift into encoding the role claim differently.
"""

from rest_framework_simplejwt.tokens import RefreshToken


def issue_tokens_for(user, role):
    # RefreshToken.for_user() only reads user.id internally to set the
    # token's user_id claim — it doesn't require AbstractBaseUser. Our
    # plain Student/Company/Officer models (regular models.Model) satisfy
    # that with no extra work.
    refresh = RefreshToken.for_user(user)
    refresh["role"] = role
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
