from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

# Get the custom or default User model
User = get_user_model() 

# --- 1. Custom Profile Extension ---
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
    location = models.CharField(max_length=100, blank=True, help_text="City and State/Region")
    bio = models.TextField(blank=True, help_text="A short description about the user/seller.")

    #This will require AWS S3 to work
    # profile_image = models.ImageField(
    #     # The 'profiles/' path will now be a folder *inside* your S3 bucket.
    #     upload_to='profiles/', 
    #     default='profiles/default.jpg',
    #     blank=True
    # )

    reputation_score = models.IntegerField(
        default=0, 
        help_text="Accumulated score from positive/negative reviews."
    )
    
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
    
# --- 3. Item Picture Model  ---
class ItemPicture(models.Model):
    """
    Stores individual pictures for an item listing.
    A ForeignKey links each picture back to a single Item.
    """
    # Links this picture to a specific Item. If the Item is deleted, the pictures are deleted (CASCADE).
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='pictures' # Allows you to call item.pictures.all()
    )
    # image = models.ImageField(
    #     upload_to='item_images/', # Pictures will be saved to your MEDIA_ROOT/item_images/
    #     help_text="Upload a picture for the item."
    # )
    is_primary = models.BooleanField(
        default=False,
        help_text="Check if this is the main image displayed in listings."
    )
    
    class Meta:
        verbose_name = 'Item Picture'
        verbose_name_plural = 'Item Pictures'
        # Optional: Adds a constraint to enforce only one primary image per item (requires more advanced handling).
        # unique_together = ('item', 'is_primary') 

    def __str__(self):
        return f"Picture for {self.item.title}"

# --- 4. Messaging Feature Models ---

# class Conversation(models.Model):
#     """
#     Represents a thread of messages between two users regarding a specific item.
#     """
#     # A conversation is linked to two users (participants) and one item.
#     item = models.ForeignKey(
#         Item, 
#         on_delete=models.CASCADE, 
#         related_name='conversations'
#     )
#     # Using 'limit_choices_to' to ensure both participants are unique in the field.
#     participant1 = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name='conversations_started'
#     )
#     participant2 = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name='conversations_received'
#     )
    
#     # Ensures only one conversation exists between two users for a given item.
#     class Meta:
#         unique_together = ('item', 'participant1', 'participant2')

#     def __str__(self):
#         return f"Conversation about '{self.item.title}'"

# class Message(models.Model):
#     """
#     Represents an individual message within a conversation.
#     """
#     # ForeignKey to link the message back to its parent conversation thread
#     conversation = models.ForeignKey(
#         Conversation, 
#         on_delete=models.CASCADE, 
#         related_name='messages'
#     )
#     # Who sent the message
#     sender = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name='sent_messages'
#     )
#     body = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     class Meta:
#         # Order messages chronologically
#         ordering = ['timestamp']

#     def __str__(self):
#         return f"Message from {self.sender.username} at {self.timestamp.strftime('%H:%M')}"