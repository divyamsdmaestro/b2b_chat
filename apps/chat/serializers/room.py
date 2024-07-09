from rest_framework import serializers

from apps.chat.models import Room
from apps.chat.serializers import MessageSerializer
from apps.common.serializers import AppReadOnlyModelSerializer


class BaseRoomSerializer(AppReadOnlyModelSerializer):
    """Base Room model serializer."""

    class Meta:
        model = Room
        fields = [
            "id",
            "uuid",
            "name",
            "created_at",
            "modified_at",
        ]


class RoomSerializer(BaseRoomSerializer):
    """Room model serializer."""

    last_message = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True, allow_null=True)

    class Meta:
        model = Room
        exclude = []
        depth = 1

    def get_last_message(self, obj: Room):
        """Return last message."""

        return MessageSerializer(obj.related_messages.order_by("created_at").last()).data
