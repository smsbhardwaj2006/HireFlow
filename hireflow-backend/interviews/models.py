"""
Interview model. Matches PRD section 8 (Interview ID, Student, Company,
Date, Time, Venue, Status).

Linked to a specific Application rather than just Student+Company, since
a student could in principle have multiple applications with the same
company (different roles) — tying the interview to the application keeps
it unambiguous which role the interview is actually for.
"""

from django.db import models
from applications.models import Application


class Interview(models.Model):
    STATUS_CHOICES = [("scheduled", "Scheduled"), ("completed", "Completed"), ("cancelled", "Cancelled")]

    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="interview")
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"Interview: {self.application.student.name} @ {self.application.job.company.name}"
