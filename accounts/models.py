from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    access_token = models.CharField(max_length=255)
    instagram_page_id = models.CharField(max_length=255)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Change this to avoid conflict with 'auth.User.groups'
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Change this to avoid conflict with 'auth.User.user_permissions'
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username
