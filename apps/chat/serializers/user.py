from rest_framework import serializers

from apps.chat.models import Tenant, User
from apps.chat.serializers import TenantOnboardSerializer, TenantSerializer
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import (
    AppCreateModelSerializer,
    AppReadOnlyModelSerializer,
    AppSerializer,
    simple_serialize_instance,
)


class UserListSerializer(AppReadOnlyModelSerializer):
    """User model serializer."""

    tenant = TenantSerializer()
    chat_room = serializers.SerializerMethodField()

    def get_chat_room(self, obj_user):
        """Get the chat room id."""

        request = self.context.get("request", None)
        if scope_user := self.context.get("scope_user", None):
            current_user = scope_user
        elif request:
            current_user = request.user
        else:
            raise serializers.ValidationError("User is not Authorized.")

        room = obj_user.chat_room_between_users(current_user)
        return simple_serialize_instance(room, keys=["id", "uuid", "name"]) if room else None

    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "b2b_id",
            "user_id",
            "first_name",
            "last_name",
            "email",
            "image",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_expert",
            "tenant",
            "chat_room",
        ]


class UserOnboardSerializer(AppCreateModelSerializer):
    """User Onboard model serializer"""

    tenant = TenantOnboardSerializer()

    class Meta(AppCreateModelSerializer.Meta):
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "user_id",
            "tenant",
        ]

    def create(self, validated_data):
        """Create a user in chat service."""

        tenant_data = validated_data.pop("tenant")
        tenant, created = Tenant.objects.get_or_create(
            tenant_id=tenant_data["tenant_id"], defaults={"name": tenant_data["name"]}
        )
        user = User.objects.filter(tenant=tenant, user_id=validated_data["user_id"]).first()
        if not user:
            user = User.objects.create_user(**validated_data, tenant=tenant)
        return user


class UserSerializer(AppSerializer):
    """User Onboard model serializer"""

    first_name = serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    last_name = serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    email = serializers.EmailField()
    user_id = serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
