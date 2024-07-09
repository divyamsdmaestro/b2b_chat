from apps.chat.models import Message
from apps.chat.serializers import UserListSerializer
from apps.common.serializers import AppReadOnlyModelSerializer


class MessageSerializer(AppReadOnlyModelSerializer):
    """Message model serializer."""

    user = UserListSerializer()

    class Meta:
        model = Message
        exclude = []
        depth = 1
