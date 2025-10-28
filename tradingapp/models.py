from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

# Get the custom or default User model
User = get_user_model() 

# --- 1. Custom User Model and Profile Extension ---
class CustomUser(AbstractUser):
    """
    A custom user model that initially has the exact same fields as the
    default AbstractUser, but allows for easy additions later.
    """
    # No custom fields added yet.
    
    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
        
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    """
    Stores extended user information like bio, location, and reputation.
    One-to-one link to Django's built-in User model.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    reputation_score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# --- 2. Item Listing Model ---
class Item(models.Model):
    """
    Represents an item for sale on the marketplace.
    """
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used_like_new', 'Used - Like New'),
        ('used_good', 'Used - Good'),
        ('used_fair', 'Used - Fair'),
    ]
    
    # ForeignKey creates a one-to-many relationship: one user can have many items
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='listings'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='used_good')
    
    # Automatically set when the item is created
    date_posted = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# --- 3. Messaging Feature Models ---

class Conversation(models.Model):
    """
    Represents a thread of messages between two users regarding a specific item.
    """
    # A conversation is linked to two users (participants) and one item.
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE, 
        related_name='conversations'
    )
    # Using 'limit_choices_to' to ensure both participants are unique in the field.
    participant1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='conversations_started'
    )
    participant2 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='conversations_received'
    )
    
    # Ensures only one conversation exists between two users for a given item.
    class Meta:
        unique_together = ('item', 'participant1', 'participant2')

    def __str__(self):
        return f"Conversation about '{self.item.title}'"

class Message(models.Model):
    """
    Represents an individual message within a conversation.
    """
    # ForeignKey to link the message back to its parent conversation thread
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    # Who sent the message
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        # Order messages chronologically
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp.strftime('%H:%M')}"