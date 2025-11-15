from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class ChatThread(models.Model):
    THREAD_TYPES = [
        ('dm', 'Direct Message'),
        ('group', 'Group Chat'),
    ]

    name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Only used for group chats."
    )

    thread_type = models.CharField(
        max_length=10,
        choices=THREAD_TYPES,
        default='dm',
    )

    participants = models.ManyToManyField(
        User,
        related_name="chat_threads",
        blank=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def latest_message(self):
        return self.messages.order_by("-created_at").first()

    @property
    def display_name(self):
        # For group chats, show: “Group Chat (3 members)”
        if self.participants.count() > 2:
            count = self.participants.count()
            return f"Group Chat ({count} members)"

        # For 1–1 chats, show the other user’s name
        usernames = [
            u.username for u in self.participants.all()
            if u != self.requesting_user
        ]
        return usernames[0] if usernames else "Chat"

    def __str__(self):
        if self.thread_type == "dm":
            users = ", ".join(self.participants.values_list("username", flat=True))
            return f"DM({users})"
        return f"Group({self.name or 'Unnamed Group'})"


class Message(models.Model):
    MESSAGE_TYPES = [
        ('normal', 'Normal'),
        ('system', 'System'),
        ('trade', 'Trade'),
    ]

    thread = models.ForeignKey(
        ChatThread,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        null=True,
        blank=True,
    )

    content = models.TextField()

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='normal',
    )

    # Optional FK for linking system/trade messages
    related_trade = models.ForeignKey(
        "core.Trade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Message<{self.id}> ({self.message_type})"
