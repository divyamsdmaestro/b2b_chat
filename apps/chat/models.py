from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from apps.chat.managers import AppUserManagerQuerySet, CourseObjectManagerQuerySet
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, COMMON_NULLABLE_FIELD_CONFIG, BaseModel


class Tenant(BaseModel):
    """
    Model to store Tenant info from IIHT-B2B-MAIN.

    Model Fields -
        PK          - id,
        Fields      - uuid, name, b2b_id, tenant_id, image,
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_tenants"

    # Fields
    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    tenant_id = models.CharField()
    b2b_id = models.PositiveIntegerField(**COMMON_NULLABLE_FIELD_CONFIG)
    image = models.URLField(**COMMON_NULLABLE_FIELD_CONFIG, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    def __str__(self):
        """Name as string representation."""

        return self.name


class User(AbstractUser, BaseModel):
    """
    Custom User model for Chat App. Used to store minimal user info from the Main B2B app.

    Model Fields -
        PK          - id
        FKs         - groups, user_permissions
        Fields      - uuid, email, first_name, last_name, password, b2b_id, user_id, image
        Datetime    - date_joined, last_login, created_at, modified_at
        Bool        - is_staff, is_superuser, is_active

    App QuerySet Manager Methods -
        get_or_none, create_user, create_superuser
    """

    class Meta:
        constraints = [models.UniqueConstraint(fields=["email", "tenant"], name="tenant_based_unique_email")]

    objects = AppUserManagerQuerySet.as_manager()

    # FK
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    # Fields
    email = models.EmailField()
    user_id = models.CharField(unique=True)
    b2b_id = models.PositiveIntegerField(**COMMON_NULLABLE_FIELD_CONFIG)
    image = models.URLField(**COMMON_NULLABLE_FIELD_CONFIG, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    is_expert = models.BooleanField(default=False)

    username = None
    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = []

    def __str__(self):
        """Email as string representation."""

        return self.email

    def chat_room_between_users(self, other_user):
        """Get the chat room which exists between users."""

        if other_user.tenant != self.tenant or other_user == self:
            return None

        room_name_1 = f"{other_user.user_id}-{self.user_id}"
        room_name_2 = f"{self.user_id}-{other_user.user_id}"
        room = Room.objects.filter(Q(name=room_name_1) | Q(name=room_name_2)).first()
        if not room:
            room = Room.objects.create(name=room_name_1)
            room.users.add(other_user, self)
        return room


class Room(BaseModel):
    """
    A chat room model to store room information.

    Model Fields -
        PK          - id
        FKs         - users
        Fields      - uuid, name
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_rooms"

    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    users = models.ManyToManyField(User, blank=True)
    is_course_group = models.BooleanField(default=False)

    def __str__(self):
        """Name as string representation."""

        return f"Room - {self.name}"


class Message(BaseModel):
    """
    Model to store all the message information.

    Model Fields -
        PK          - id
        FKs         - room, user
        Fields      - uuid, text
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_messages"

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """User and room name as string representation."""

        return f"Message({self.user} {self.room})"


class Course(BaseModel):
    """
    Model to store Course info from IIHT-B2B-MAIN.

    Model Fields -
        PK          - id,
        Fields      - uuid, name, course_uuid, image, is_ccms
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none, ccms, no_ccms
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_courses"

    # Manager
    objects = CourseObjectManagerQuerySet.as_manager()

    # FK
    tenant: Tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, **COMMON_NULLABLE_FIELD_CONFIG)

    # Fields
    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    course_uuid = models.UUIDField(editable=False)
    image = models.URLField(**COMMON_NULLABLE_FIELD_CONFIG, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    is_ccms = models.BooleanField(default=False)

    def __str__(self):
        """Name as string representation."""

        return self.name

    @classmethod
    def init_course(cls, tenant, **kwargs):
        """DRY create code."""

        course, created = Course.objects.update_or_create(
            course_uuid=kwargs.pop("course_uuid"), tenant=tenant, defaults=kwargs
        )
        course.chat_room()
        return course

    def chat_room(self):
        """Get the chat room for the course."""

        if not self.room:
            unique_name = f"{self.tenant.tenant_id}:{self.course_uuid}"
            self.room = Room.objects.create(name=unique_name, is_course_group=True)
            self.save()
        return self.room


class CourseExpert(BaseModel):
    """
    Model to store all the Expert Users for the Course.

    Model Fields -
        PK          - id
        FKs         - course, user
        Fields      - uuid
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_course_experts"

    tenant: Tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        """User and room name as string representation."""

        return f"{self.course.name} - {self.user.first_name}"
