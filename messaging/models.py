from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class ChatThread(models.Model):
    participants = models.ManyToManyField(User, related_name="chat_threads")
    created_at = models.DateTimeField(auto_now_add=True)

    # makes sure a chat thread has only two users
    def clean(self) -> None:
        if self.pk and self.participants.count() > 2:
            raise ValidationError("A chat thread can only have two users.")

    # returns username attached to chat thread
    def __str__(self) -> str:
        usernames = ", ".join(sorted(self.participants.values_list("username", flat=True)))
        return f"ChatThread({usernames})"


class Message(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages", null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"Message<{self.id}> from {self.sender} in thread {self.thread_id}"