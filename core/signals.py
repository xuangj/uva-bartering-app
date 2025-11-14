from django.contrib.auth.models import User
from core.models import SustainabilityInterests, TradingInterests
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# Hard-coded interests inserted into tables
@receiver(post_migrate)
def populate_default_interests(sender, **kwargs):
    SUSTAINABILITY_INTERESTS = [
        "Upcycling",
        "Recycling",
        "Thrifting",
        "Gardening",
        "Reusing",
        "Foraging",
    ]

    TRADING_INTERESTS = [
        "Clothes",
        "Books",
        "Furniture",
        "Kitchenware",
        "Knick-knacks",
        "Electronics",
        "Swag",
        "Free stuff",
    ]
    
    if sender.name == "core":
        for name in SUSTAINABILITY_INTERESTS:
            SustainabilityInterests.objects.get_or_create(name=name)
        for name in TRADING_INTERESTS:
            TradingInterests.objects.get_or_create(name=name)