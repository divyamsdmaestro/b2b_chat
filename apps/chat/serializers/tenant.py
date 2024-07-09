from apps.chat.models import Tenant
from apps.common.serializers import AppCreateModelSerializer, AppReadOnlyModelSerializer


class TenantSerializer(AppReadOnlyModelSerializer):
    """Tenant model serializer."""

    class Meta:
        model = Tenant
        fields = [
            "id",
            "uuid",
            "b2b_id",
            "tenant_id",
            "name",
            "image",
        ]


class TenantOnboardSerializer(AppCreateModelSerializer):
    """Tenant On-board model serializer."""

    class Meta(AppCreateModelSerializer.Meta):
        model = Tenant
        fields = ["tenant_id", "name"]
