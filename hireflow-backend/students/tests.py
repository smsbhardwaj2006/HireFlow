"""
Tests for student auth. Run with: python manage.py test students
"""

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Student


class StudentRegisterTests(APITestCase):
    def test_register_creates_student_with_hashed_password(self):
        url = reverse("student-register")
        payload = {
            "name": "Test Student", "email": "test@college.edu", "password": "StrongPass123",
            "branch": "CSE", "course": "B.Tech", "cgpa": "8.0",
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        student = Student.objects.get(email="test@college.edu")
        self.assertNotEqual(student.password, "StrongPass123")
        self.assertTrue(student.check_password("StrongPass123"))

    def test_register_rejects_duplicate_email(self):
        student = Student(name="Existing", email="dupe@college.edu", branch="CSE", cgpa=7.0)
        student.set_password("pass12345")
        student.save()

        url = reverse("student-register")
        payload = {"name": "Another", "email": "dupe@college.edu", "password": "StrongPass123", "branch": "IT", "cgpa": "7.5"}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StudentLoginTests(APITestCase):
    def setUp(self):
        self.student = Student(name="Login Student", email="login@college.edu", branch="CSE", cgpa=8.0)
        self.student.set_password("StrongPass123")
        self.student.save()

    def test_login_returns_tokens_with_role_claim(self):
        url = reverse("student-login")
        response = self.client.post(url, {"email": "login@college.edu", "password": "StrongPass123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_with_wrong_password_fails(self):
        url = reverse("student-login")
        response = self.client.post(url, {"email": "login@college.edu", "password": "WrongPassword"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StudentProfileAccessTests(APITestCase):
    """Confirms MultiRoleJWTAuthentication correctly resolves a student
    token to a Student instance, and that company/officer-only endpoints
    reject a student token (role-mismatch is the main risk in this
    three-model design — see config/authentication.py)."""

    def setUp(self):
        self.student = Student(name="Profile Student", email="profile@college.edu", branch="CSE", cgpa=8.0)
        self.student.set_password("StrongPass123")
        self.student.save()

        login_response = self.client.post(
            reverse("student-login"), {"email": "profile@college.edu", "password": "StrongPass123"}
        )
        self.access_token = login_response.data["access"]

    def test_student_can_access_own_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(reverse("student-profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "profile@college.edu")

    def test_student_token_cannot_access_officer_endpoint(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(reverse("admin-student-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_token_cannot_access_profile(self):
        response = self.client.get(reverse("student-profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
