"""
Officer model.

Unlike Student and Company, Officer subclasses AbstractBaseUser. Why the
inconsistency: settings.AUTH_USER_MODEL has to point at *some* model for
Django's admin site and permission framework to function, and officers —
who manage the whole system and are the only role meant to use /admin/ —
are the natural choice. This still doesn't make Officer "the" user model
in the way ShopSphere's single User model was; Student and Company remain
fully independent tables with their own login flow through the custom
JWT auth in config/authentication.py. Officer just additionally satisfies
Django's internal expectations so /admin/ works.

Officers are NOT self-registered (PRD section 4 lists officer-managed
actions like "Approve Company Registration" but no officer self-signup).
Create the first one with: python manage.py create_officer
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class OfficerManager(BaseUserManager):
    def create_officer(self, email, name, password):
        if not email:
            raise ValueError("Officers must have an email address.")
        officer = self.model(email=self.normalize_email(email), name=name)
        officer.set_password(password)
        officer.is_staff = True  # lets them into /admin/
        officer.is_superuser = True  # officers manage the whole system per PRD
        officer.save(using=self._db)
        return officer

    def create_superuser(self, email, name=None, password=None, **extra_fields):
        # Satisfies `python manage.py createsuperuser`'s expectations,
        # since AUTH_USER_MODEL points here.
        return self.create_officer(email, name or "Officer", password)


class Officer(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = OfficerManager()

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
