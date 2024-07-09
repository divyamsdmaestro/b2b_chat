from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager

from apps.common.managers import BaseObjectManagerQuerySet


class AppUserManagerQuerySet(BaseObjectManagerQuerySet, UserManager):
    """Custom manager for the User model."""

    def _create_user(self, email: str, password: str | None, **extra_fields):
        """Create and save a user with the given email and password."""

        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save app user."""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        """Create and save app superuser."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CourseObjectManagerQuerySet(BaseObjectManagerQuerySet):
    """
    Custom QuerySet for Course Model.

    Usage on the model class -
        objects = CourseObjectManagerQuerySet.as_manager()

    Available methods -
        get_or_none
    """

    def ccms(self):
        """Return a queryset of only the ccms courses."""

        return self.filter(is_ccms=True)

    def no_ccms(self):
        """Return a queryset of only the tenant courses."""

        return self.filter(is_ccms=False)
