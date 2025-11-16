from django.db import models
from django.contrib.auth.models import User

from core.models import Post, Report, Profile


# Moderation action log
class ModerationAction(models.Model):
    ACTION_TYPES = [
        ("ban", "Ban User"),
        ("unban", "Unban User"),
        ("delete_post", "Delete Post"),
        ("warn_user", "Warn User"),
        ("resolve_report", "Resolve Report"),
        ("dismiss_report", "Dismiss Report"),
        ("system", "System Action"),
    ]

    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="moderator_actions",
        help_text="The moderator who performed the action."
    )

    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions_taken_against",
        help_text="User affected by this action."
    )

    target_post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mod_actions",
        help_text="Post affected by moderation."
    )

    target_report = models.ForeignKey(
        Report,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mod_actions",
        help_text="Report associated with this action."
    )

    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    reason = models.TextField(blank=True, help_text="Optional explanation of the action.")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.target_user.username if self.target_user else "N/A"
        return f"{self.get_action_type_display()} on {target} ({self.created_at.date()})"


# Way to process reports
class ReportResolution(models.Model):
    STATUS = [
        ("open", "Open"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
    ]

    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name="resolution",
    )

    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports_resolved",
    )

    status = models.CharField(max_length=20, choices=STATUS, default="open")
    notes = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.report.id}: {self.status}"


# Attach private notes to users/posts
class ModeratorNote(models.Model):
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notes_written"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="moderator_notes"
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="moderator_notes"
    )

    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = (
            self.user.username if self.user
            else f"Post {self.post.id}" if self.post
            else "Unknown"
        )
        return f"Note on {target} ({self.created_at.date()})"
