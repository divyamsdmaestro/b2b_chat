from rest_framework import serializers

from apps.chat.models import Course, User
from apps.chat.serializers import TenantSerializer, UserSerializer
from apps.chat.serializers.room import BaseRoomSerializer
from apps.common.serializers import AppReadOnlyModelSerializer, AppSerializer


class CourseListSerializer(AppReadOnlyModelSerializer):
    """Course model List serializer."""

    tenant = TenantSerializer()
    chat_room = BaseRoomSerializer()

    class Meta:
        model = Course
        fields = [
            "id",
            "uuid",
            "name",
            "course_uuid",
            "is_ccms",
            "image",
            "tenant",
            "chat_room",
        ]


class CourseSerializer(AppSerializer):
    """Serializer class for course create."""

    course_uuid = serializers.CharField()
    name = serializers.CharField()
    image = serializers.URLField(required=False, allow_null=True)
    is_ccms = serializers.BooleanField(default=False)

    def save(self, **kwargs):
        """Save Course based on tenant."""

        tenant = self.get_user().tenant
        return Course.init_course(tenant, **self.validated_data)


class CourseEnrollSerializer(CourseSerializer):
    """Serializer class for enrolling to a Course."""

    is_expert = serializers.BooleanField(default=False)
    user_id = serializers.ListField(child=serializers.CharField())

    def save(self, **kwargs):
        """Save Course based on tenant."""

        is_expert = self.validated_data.pop("is_expert")
        user_ids = self.validated_data.pop("user_id")
        for user_id in user_ids:
            user = User.objects.filter(user_id=user_id).first()
            if user:
                tenant = user.tenant
                course = Course.init_course(tenant, **self.validated_data)
                room = course.chat_room()
                if user not in room.users.all():
                    room.users.add(user)
                if is_expert:
                    course.related_course_experts.get_or_create(user=user, tenant=tenant)
        return True


class CourseExpertSerializer(CourseSerializer):
    """Serializer class to add an expert."""

    user = UserSerializer()

    def save(self, **kwargs):
        """Save the expert to the course."""

        tenant = self.get_user().tenant
        user_data = self.validated_data.pop("user")
        user_id = user_data.pop("user_id", None)
        course = Course.init_course(tenant, **self.validated_data)
        user, created = User.objects.update_or_create(tenant=tenant, user_id=user_id, defaults=user_data)
        course.related_course_experts.get_or_create(user=user, tenant=tenant)
        return True
