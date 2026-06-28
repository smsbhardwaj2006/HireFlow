"""
Application model. Matches PRD section 8 (Application: Application ID,
Student, Job, Status, Applied Date) and PRD section 4's status list
exactly: Applied -> Under Review -> Shortlisted -> Interview Scheduled ->
Selected, with Rejected branching off at any point.

The STATUS_CHOICES order below intentionally matches the frontend's
STATUS_FLOW array in hireflow/js/data.js so the pipeline visualization on
both sides describes the same five steps — important if this backend
later replaces the frontend's localStorage simulation.
"""

from django.db import models
from students.models import Student
from jobs.models import Job


class Application(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("review", "Under Review"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview Scheduled"),
        ("selected", "Selected"),
        ("rejected", "Rejected"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    applied_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ["student", "job"]  # one application per student per job
        ordering = ["-applied_date"]

    def __str__(self):
        return f"{self.student.name} -> {self.job.title} ({self.status})"
