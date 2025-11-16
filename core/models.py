# core/models.py

import os
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Denied', 'Denied'),
]

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
    nickname = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True, max_length=100)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='undergrad')
    sustainability_interests = models.ManyToManyField(SustainabilityInterests, blank=True)
    trading_interests = models.ManyToManyField(TradingInterests, blank=True)
    pfp = models.ImageField(upload_to=unique_post_image_path, blank=True, null=True)
    banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(null=True, blank=True)

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
    # The user who initiates the trade
    offerer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trades_made"
    )

    # The owner of the requested post
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trades_received"
    )

    # The post being requested
    item_requested = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="trades_offered_on"
    )

    # The posts the offerer is putting up in exchange
    offered_posts = models.ManyToManyField(
        Post,
        related_name="trades_offered_with"
    )

    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    class Meta:
        # Only one *pending* trade per (offerer, item_requested)
        constraints = [
            models.UniqueConstraint(
                fields=['offerer', 'item_requested'],
                condition=Q(status='Pending'),
                name='unique_pending_trade_per_user_and_post',
            )
        ]

    def __str__(self):
        return f"{self.offerer.username} → {self.receiver.username} for {self.item_requested.title}"

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
    
