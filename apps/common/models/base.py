import uuid
from contextlib import suppress

from django.core.exceptions import FieldDoesNotExist
from django.db import models

from apps.common.managers import BaseObjectManagerQuerySet

# top level config
COMMON_CHAR_FIELD_MAX_LENGTH = 512
COMMON_NULLABLE_FIELD_CONFIG = {  # user for API based stuff
    "default": None,
    "null": True,
}
COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG = {  # user for Form/app based stuff
    **COMMON_NULLABLE_FIELD_CONFIG,
    "blank": True,
}


class BaseModel(models.Model):
    """
    Contains the last modified and the created fields, basically
    the base model for the entire app.

    ********************* Model Fields *********************
    PK -
        id
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
    """

    # unique id field
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    # time tracking
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # custom manager
    objects = BaseObjectManagerQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        abstract = True

    @classmethod
    def get_model_fields(cls):
        """
        Returns all the model fields. This does not
        include the defined M2M & related fields.
        """

        return cls._meta.fields

    @classmethod
    def get_all_model_fields(cls):
        """
        Returns all model fields, this includes M2M and related fields.
        Note: The field classes will be different & additional here.
        """

        return cls._meta.get_fields()

    @classmethod
    def get_model_field_names(cls, exclude=[]):  # noqa
        """Returns only the flat field names of the model."""

        exclude = ["id", "created_by", "created", "modified", *exclude]
        return [_.name for _ in cls.get_model_fields() if _.name not in exclude]

    @classmethod
    def get_model_field(cls, field_name, fallback=None):
        """Returns a single model field given by `field_name`."""

        with suppress(FieldDoesNotExist):
            return cls._meta.get_field(field_name)

        return fallback


class FileOnlyModel(BaseModel):
    """
    Parent class for all the file only models. This is used as a common class
    and for differentiating field on the run time.

    This will contain only:
        file = model_fields.AppFileField(...)

    This model is then linked as a foreign key where ever necessary.

    ********************* Model Fields *********************
    PK -
        id
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
    """

    class Meta(BaseModel.Meta):
        abstract = True
