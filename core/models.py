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
    CATEGORY = [
        ('Electronics','Electronics'),
        ('Books','Books'),
        ('Clothing','Clothing'),
        ('Furniture','Furniture'),
        ('Food','Food'),
        ('First-year','First-year'),
        ('Swag','Swag'),
        ('Plants','Plants'),
        ('Miscellaneous', 'Miscellaneous'),
    ]

    
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to=unique_post_image_path, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY, default='Miscellaneous')
    price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Report(models.Model):
    # The user who filed the report (ForeignKey to User or Profile)
    # Assuming 'reporter' is linked directly to the standard Django User
    reporter = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reports_filed'
    )
    
    # The user whose account/post is being reported
    reported_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reports_received'
    )
    
    # The specific post being reported (ForeignKey to Post)
    reported_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE, 
        related_name='reports'
    )
    
    # The reason for the report
    comments = models.TextField(verbose_name='Reason for Report')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter.username} on Post {self.reported_post.id}"
    
