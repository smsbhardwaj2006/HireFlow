"""
Job model. Matches PRD section 8 (Job table: Job ID, Company, Title,
Description, Location, Salary, Eligibility, Deadline).

Eligibility is stored as two explicit fields (min_cgpa, eligible_branches)
rather than free text, specifically so eligibility filtering — "only show
students jobs they actually qualify for" — can be a real database query
(see is_eligible_for below and the student-facing list view in views.py)
instead of something that has to be parsed out of a text blob.
"""

from django.db import models
from companies.models import Company


class Job(models.Model):
    TYPE_CHOICES = [("full_time", "Full-time"), ("internship", "Internship")]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=120)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="full_time")

    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    eligible_branches = models.JSONField(default=list, blank=True)  # e.g. ["CSE", "IT"]

    deadline = models.DateField()
    drive_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["company"]), models.Index(fields=["deadline"])]

    def __str__(self):
        return f"{self.title} @ {self.company.name}"

    def is_eligible_for(self, student):
        if student.cgpa < self.min_cgpa:
            return False
        if self.eligible_branches and student.branch not in self.eligible_branches:
            return False
        return True
