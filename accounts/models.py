from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model with premium feature flag.
    Extends Django's built-in user to add payment tracking.
    """
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[],
        help_text="Required. 150 characters or fewer. Any characters allowed.",
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    is_premium = models.BooleanField(
        default=False,
        help_text="Premium users can upload media and share notes"
    )
    premium_activated_at = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, help_text="M-Pesa phone number")
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'