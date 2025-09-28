from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    email = models.EmailField('email address', unique=True)
    is_confirmed = models.BooleanField('email confirmed', default=False)
    confirmation_token = models.CharField(max_length=100, blank=True, null=True)
    confirmation_sent_at = models.DateTimeField(null=True, blank=True)
    
    # For future subscription functionality
    subscription_tier = models.CharField(
        max_length=20,
        choices=[('free', 'Free'), ('basic', 'Basic'), ('pro', 'Professional')],
        default='free'
    )
    subscription_expires = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
