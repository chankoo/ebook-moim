import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user():
    """
    Test creating a new user with the custom manager.
    """
    user = User.objects.create_user(
        instagram_id="test_ig_id",
        username="testuser",
        password="testpassword123",
    )
    assert user.instagram_id == "test_ig_id"
    assert user.username == "testuser"
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.check_password("testpassword123") is True


@pytest.mark.django_db
def test_create_user_without_instagram_id_raises_error():
    """
    Test that creating a user without an instagram_id raises a ValueError.
    """
    with pytest.raises(ValueError, match="Users must have an instagram_id"):
        User.objects.create_user(
            instagram_id=None,
            username="testuser",
            password="testpassword123",
        )


@pytest.mark.django_db
def test_create_superuser():
    """
    Test creating a new superuser with the custom manager.
    """
    superuser = User.objects.create_superuser(
        instagram_id="super_ig_id",
        username="superuser",
        password="superpassword123",
    )
    assert superuser.instagram_id == "super_ig_id"
    assert superuser.username == "superuser"
    assert superuser.is_active is True
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.check_password("superpassword123") is True


@pytest.mark.django_db
def test_create_superuser_with_is_staff_false_raises_error():
    """
    Test that creating a superuser with is_staff=False raises a ValueError.
    """
    with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
        User.objects.create_superuser(
            instagram_id="super_ig_id",
            username="superuser",
            password="superpassword123",
            is_staff=False,
        )


@pytest.mark.django_db
def test_create_superuser_with_is_superuser_false_raises_error():
    """
    Test that creating a superuser with is_superuser=False raises a ValueError.
    """
    with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
        User.objects.create_superuser(
            instagram_id="super_ig_id",
            username="superuser",
            password="superpassword123",
            is_superuser=False,
        )