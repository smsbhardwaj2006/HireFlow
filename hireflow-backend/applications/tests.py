"""
Tests for the application workflow — the core business logic of this
backend. Run with: python manage.py test applications
"""

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from students.models import Student
from companies.models import Company
from jobs.models import Job
from .models import Application


class ApplyToJobTests(APITestCase):
    def setUp(self):
        self.company = Company(name="Test Co", email="hr@testco.com", status="approved")
        self.company.set_password("pass12345")
        self.company.save()

        self.job = Job.objects.create(
            company=self.company, title="Test Role", location="Remote", salary=500000,
            min_cgpa=7.0, eligible_branches=["CSE"], deadline="2026-12-31",
        )

        self.student = Student(name="Eligible Student", email="eligible@college.edu", branch="CSE", cgpa=8.0)
        self.student.set_password("pass12345")
        self.student.resume = "resumes/test.pdf"  # simulate a resume already uploaded
        self.student.save()

        login = self.client.post(reverse("student-login"), {"email": "eligible@college.edu", "password": "pass12345"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_eligible_student_can_apply(self):
        response = self.client.post(reverse("apply-to-job"), {"job_id": self.job.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(Application.objects.first().status, "applied")

    def test_cannot_apply_twice_to_same_job(self):
        self.client.post(reverse("apply-to-job"), {"job_id": self.job.id})
        response = self.client.post(reverse("apply-to-job"), {"job_id": self.job.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Application.objects.count(), 1)

    def test_ineligible_branch_cannot_apply(self):
        ineligible = Student(name="Wrong Branch", email="wrongbranch@college.edu", branch="MECH", cgpa=9.0)
        ineligible.set_password("pass12345")
        ineligible.resume = "resumes/test2.pdf"
        ineligible.save()

        login = self.client.post(reverse("student-login"), {"email": "wrongbranch@college.edu", "password": "pass12345"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.post(reverse("apply-to-job"), {"job_id": self.job.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_apply_without_resume(self):
        no_resume = Student(name="No Resume", email="noresume@college.edu", branch="CSE", cgpa=8.0)
        no_resume.set_password("pass12345")
        no_resume.save()

        login = self.client.post(reverse("student-login"), {"email": "noresume@college.edu", "password": "pass12345"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.post(reverse("apply-to-job"), {"job_id": self.job.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateApplicationStatusTests(APITestCase):
    """The key risk here: company A must never be able to update an
    application against company B's job, even by guessing an application
    id. UpdateApplicationStatusView filters by job__company=request.user
    specifically to prevent that."""

    def setUp(self):
        self.company_a = Company(name="Company A", email="a@company.com", status="approved")
        self.company_a.set_password("pass12345")
        self.company_a.save()

        self.company_b = Company(name="Company B", email="b@company.com", status="approved")
        self.company_b.set_password("pass12345")
        self.company_b.save()

        self.job_a = Job.objects.create(
            company=self.company_a, title="Job A", location="Remote", salary=500000,
            min_cgpa=0, eligible_branches=["CSE"], deadline="2026-12-31",
        )

        student = Student(name="Applicant", email="applicant@college.edu", branch="CSE", cgpa=8.0)
        student.set_password("pass12345")
        student.save()

        self.application = Application.objects.create(student=student, job=self.job_a)

        login_b = self.client.post(reverse("company-login"), {"email": "b@company.com", "password": "pass12345"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_b.data['access']}")

    def test_company_cannot_update_another_companys_application(self):
        url = reverse("application-status", kwargs={"pk": self.application.id})
        response = self.client.put(url, {"status": "shortlisted"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "applied")  # unchanged

    def test_owning_company_can_update_application(self):
        login_a = self.client.post(reverse("company-login"), {"email": "a@company.com", "password": "pass12345"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_a.data['access']}")

        url = reverse("application-status", kwargs={"pk": self.application.id})
        response = self.client.put(url, {"status": "shortlisted"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "shortlisted")
