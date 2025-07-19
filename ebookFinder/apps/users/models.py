from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, instagram_id, username, password=None, **extra_fields):
        if not instagram_id:
            raise ValueError("Users must have an instagram_id")

        user = self.model(
            instagram_id=instagram_id,
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, instagram_id, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(instagram_id, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    instagram_id = models.CharField(max_length=255, unique=True, null=True)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "instagram_id"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username
