"""
Student auth + profile views.

POST /api/students/register   -> create account
POST /api/students/login      -> JWT tokens (role="student" claim)
GET/PUT /api/students/profile -> view/edit own profile
POST /api/students/resume     -> upload resume (PDF)
"""

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from config.tokens import issue_tokens_for
from officers.permissions import IsOfficer
from .models import Student
from .serializers import StudentRegisterSerializer, StudentLoginSerializer, StudentProfileSerializer
from .permissions import IsStudent


class StudentRegisterView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        tokens = issue_tokens_for(student, "student")
        return Response(
            {"message": "Account created.", "user": StudentProfileSerializer(student).data, **tokens},
            status=status.HTTP_201_CREATED,
        )


class StudentLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = StudentLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            student = Student.objects.get(email__iexact=email)
        except Student.DoesNotExist:
            return Response({"error": "No student account matches those credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not student.check_password(password):
            return Response({"error": "No student account matches those credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = issue_tokens_for(student, "student")
        return Response({"user": StudentProfileSerializer(student).data, **tokens})


class StudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_object(self):
        return self.request.user


class StudentResumeUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def post(self, request):
        student = request.user
        file = request.FILES.get("resume")
        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        if file.content_type != "application/pdf":
            return Response({"error": "Resume must be a PDF file."}, status=status.HTTP_400_BAD_REQUEST)

        student.resume = file
        student.save(update_fields=["resume"])
        return Response(StudentProfileSerializer(student).data)

    def delete(self, request):
        student = request.user
        student.resume = None
        student.save(update_fields=["resume"])
        return Response(StudentProfileSerializer(student).data)


# ──────────────────────────────────────────────────────────────────────────
# Officer-only: manage students (PRD section 4 — Officer can Add/Edit/
# Delete/View students). Separate from the student's own profile endpoint
# above, which only ever touches request.user's own record.
# ──────────────────────────────────────────────────────────────────────────

class AdminStudentListCreateView(generics.ListCreateAPIView):
    """GET: officer views all students. POST: officer manually adds one
    (e.g. for a student who hasn't self-registered yet)."""

    queryset = Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOfficer]

    def get_serializer_class(self):
        return StudentRegisterSerializer if self.request.method == "POST" else StudentProfileSerializer

    def perform_create(self, serializer):
        # Officer-added students get a random placeholder password; in a
        # real deployment you'd email the student a reset link instead.
        import secrets
        serializer.save()
        student = serializer.instance
        student.set_password(secrets.token_urlsafe(12))
        student.save(update_fields=["password"])


class AdminStudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOfficer]

