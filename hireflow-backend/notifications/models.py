"""
Notification model. Matches PRD section 8 (Notification ID, Title,
Message, Date) and section 6 (Officer can send announcements about New
Drives, Interviews, Deadlines, Placement Results).

Broadcast-only for now (one notification reaches all students) rather than
per-student read/unread tracking — the PRD's Officer Module describes
"Send announcements" as a broadcast action, and per-student delivery
tracking would be a reasonable Phase 2 if read-receipts mattered.
"""

from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ("drive", "New Drive"),
        ("deadline", "Deadline Reminder"),
        ("interview", "Interview Update"),
        ("result", "Placement Result"),
    ]

    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="drive")
    title = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title
