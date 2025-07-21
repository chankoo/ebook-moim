from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self, username, password=None, instagram_id=None, email=None, **extra_fields
    ):
        if not instagram_id and not email:
            raise ValueError("Users must have an instagram_id or an email")

        if email:
            email = self.normalize_email(email)
            extra_fields.setdefault("email", email)

        user = self.model(
            instagram_id=instagram_id,
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # For superuser, we might require an email and a dummy instagram_id
        extra_fields.setdefault("email", "admin@example.com")
        extra_fields.setdefault("instagram_id", "admin_user")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username=username, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    instagram_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "instagram_id"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username
