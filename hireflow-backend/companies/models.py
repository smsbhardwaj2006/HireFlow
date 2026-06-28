"""
Company model. See students/models.py for why this is its own model
rather than a role flag on a shared User table.

New companies register with status="pending" and can't have their jobs
shown to students until a Placement Officer approves them (PRD section 4:
officer can "Approve Company Registration"). See officers/views.py for
the approve endpoint, and jobs/views.py for where pending-company jobs
get filtered out of student-facing listings.
"""

from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Company(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("approved", "Approved")]

    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} ({self.status})"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        return True
