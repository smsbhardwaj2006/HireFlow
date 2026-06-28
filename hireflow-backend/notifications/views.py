"""
Notification views.

GET  /api/notifications  -> list all (any logged-in role can read — students,
                             companies, and officers all see announcements)
POST /api/notifications  -> officer sends a new announcement
"""

from rest_framework import generics, permissions

from officers.permissions import IsOfficer
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListCreateView(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsOfficer()]
        return [permissions.IsAuthenticated()]
