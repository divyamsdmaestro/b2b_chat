from rest_framework.permissions import IsAuthenticated

from ..common.views.api import AppAPIView, AppModelCreatePIViewSet, AppModelListAPIViewSet
from ..common.views.api.base import UserTenantMixin
from .models import Course, User
from .serializers import (
    CourseEnrollSerializer,
    CourseExpertSerializer,
    CourseListSerializer,
    CourseSerializer,
    UserListSerializer,
    UserOnboardSerializer,
)


class UserListAPIView(UserTenantMixin, AppModelListAPIViewSet):
    """View to list down all the `User`."""

    serializer_class = UserListSerializer
    get_object_model = User
    queryset = User.objects.all()
    all_table_columns = {}
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_expert", "user_id", "b2b_id"]
    search_fields = ["first_name", "last_name", "email"]

    def get_queryset(self):
        """Filter based on course if course key is passed."""

        queryset = super().get_queryset()
        if course_uuid := self.request.query_params.get("course_uuid"):
            queryset = queryset.filter(
                related_course_experts__course__course_uuid=course_uuid,
                related_course_experts__tenant=self.get_user().tenant,
            )
        return queryset


class UserOnboardAPIViewSet(AppModelCreatePIViewSet):
    """View to onboard a user."""

    queryset = User.objects.all()
    serializer_class = UserOnboardSerializer


class CourseListAPIView(UserTenantMixin, AppModelListAPIViewSet):
    """View to list down all the `Courses`."""

    serializer_class = CourseListSerializer
    get_object_model = Course
    queryset = Course.objects.all()
    all_table_columns = {}
    permission_classes = [IsAuthenticated]
    filterset_fields = ["name", "course_uuid"]
    search_fields = ["name"]

    def get_queryset(self):
        """Filter qs based on user enrollment."""

        qs = super().get_queryset()
        return qs.filter(room__users__id__in=[self.get_user().id])


class CourseCUDApiView(AppAPIView):
    """Api view to create the course."""

    serializer_class = CourseSerializer

    def post(self, request, *args, **kwargs):
        """Perform the expert approval."""

        serializer = self.get_valid_serializer()
        serializer.save()
        return self.send_response(data="Action performed successfully.")


class CourseEnrollApiView(AppAPIView):
    """Api view to add the user to the course."""

    serializer_class = CourseEnrollSerializer

    def post(self, request, *args, **kwargs):
        """Perform the expert approval."""

        serializer = self.get_valid_serializer()
        serializer.save()
        return self.send_response(data="Action performed successfully.")


class CourseExpertApiView(AppAPIView):
    """Api view to add the expert to the course."""

    serializer_class = CourseExpertSerializer

    def post(self, request, *args, **kwargs):
        """Perform the expert approval."""

        serializer = self.get_valid_serializer()
        serializer.save()
        return self.send_response(data="Action performed successfully.")
