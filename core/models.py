# core/models.py
import os
import uuid

from django.contrib.auth.models import User
from django.db import models

# --- Helper functions --- #


def unique_post_image_path(instance, filename):
    """Generate unique file path for each uploaded post image."""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("posts", filename)


# --- Database scheme --- #    

class SustainabilityInterests(models.Model):
    name = models.CharField(max_length=150, unique=True)
    
    def __str__(self):
        return self.name


class TradingInterests(models.Model):
    name = models.CharField(max_length=150, unique=True)
    
    def __str__(self):
        return self.name
    


class Profile(models.Model):
    ROLE_CHOICES = [
        ('Undergraduate Student', 'Undergraduate Student'),
        ('Graduate Student', 'Graduate Student'),
        ('Faculty', 'Faculty'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='undergrad')
    sustainability_interests = models.ManyToManyField(SustainabilityInterests, blank=True)
    trading_interests = models.ManyToManyField(TradingInterests, blank=True)
    def __str__(self):
        return self.user.username
    

class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=100)
    item_offered = models.CharField(max_length=100, default=title)
    description = models.TextField()
    image = models.ImageField(upload_to=unique_post_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} from {self.poster.username}"


class Trade(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Denied', 'Denied'),
    ]

    userOne = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trades_initiated")
    userTwo = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trades_received")
    
    post_reference = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    item_offered = models.CharField(max_length=100)
    item_requested = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="item_requested")
    image = models.ImageField(upload_to=unique_post_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    comment = models.TextField()

    def __str__(self):
        return f"{self.userOne.username} to {self.userTwo.username}"
