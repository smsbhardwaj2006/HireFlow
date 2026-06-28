"""
Student model.

This is deliberately NOT a Django AbstractUser subclass. The PRD treats
Student, Company, and Officer as three genuinely separate kinds of account
with different fields and different logins — forcing them into one User
table with a role flag would mean every table has a pile of nullable
columns that only make sense for one role (a Company has no CGPA, a
Student has no website). Three small, focused tables map onto the PRD's
own schema (section 8) much more directly, at the cost of needing the
custom multi-role JWT auth in config/authentication.py instead of Django's
built-in single-user-model assumptions.

Password hashing still uses Django's make_password/check_password
utilities directly (see serializers.py) since we're not subclassing
AbstractBaseUser here.
"""

from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Student(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # always stored hashed — see set_password()
    phone = models.CharField(max_length=15, blank=True)
    branch = models.CharField(max_length=50)
    course = models.CharField(max_length=50, default="B.Tech")
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    skills = models.JSONField(default=list, blank=True)  # simple list of strings; fine for this scale
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} <{self.email}>"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def profile_completion(self):
        # Mirrors the frontend's profileComplete scoring exactly, so a
        # student sees the same number whether it's computed by the demo
        # frontend or this real backend.
        score = 20
        if self.phone:
            score += 15
        if self.skills:
            score += 20
        if self.resume:
            score += 30
        if self.cgpa:
            score += 15
        return min(100, score)

    # DRF permission classes check these to know "is this request
    # authenticated, and as what". See MultiRoleJWTAuthentication, which
    # sets is_authenticated implicitly by returning a real instance.
    @property
    def is_authenticated(self):
        return True
