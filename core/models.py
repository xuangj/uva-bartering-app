# core/models.py
import os
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
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

    # 1. Choices for ALL items (Big to Small)
    GENERAL_SIZES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]

    # 2. Choices for ALL items (Heavy to Light)
    WEIGHT_CATEGORIES = [
        ('L', 'Light'),
        ('M', 'Medium'),
        ('H', 'Heavy'),
    ]

    # 3. Choices ONLY for Clothing category
    CLOTHING_SIZES = [
        ('XS', 'Extra Small (XS)'),
        ('S', 'Small (S)'),
        ('M', 'Medium (M)'),
        ('L', 'Large (L)'),
        ('XL', 'Extra Large (XL)'),
        ('XXL', 'Double Extra Large (XXL)'),
    ]
    
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    item_offered = models.CharField(max_length=100, default=title)
    description = models.TextField()
    image = models.ImageField(upload_to=unique_post_image_path, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY, default='Miscellaneous')
    general_size = models.CharField(max_length=5, choices=GENERAL_SIZES, default='M',verbose_name='Item Size (General)')
    weight = models.CharField(max_length=5, choices=WEIGHT_CATEGORIES, default='M',verbose_name='Item Weight')
    clothing_size = models.CharField(max_length=5, choices=CLOTHING_SIZES, blank=True, null=True,verbose_name='Clothing Size')
    price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.category == 'Clothing' and not self.clothing_size:
            raise ValidationError({'clothing_size': 'Clothing size is required for items in the Clothing category.'})
        if self.category != 'Clothing' and self.clothing_size:
            self.clothing_size = None  # Clear clothing_size if not in Clothing category
    
    def __str__(self):
        return self.title

class Trade(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Denied', 'Denied'),
    ]

    userOne = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trades_initiated")
    userTwo = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trades_received")

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
