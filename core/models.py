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
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to=unique_post_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
