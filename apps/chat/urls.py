from django.urls import path

from ..common.routers import AppSimpleRouter
from .views import (
    CourseCUDApiView,
    CourseEnrollApiView,
    CourseExpertApiView,
    CourseListAPIView,
    UserListAPIView,
    UserOnboardAPIViewSet,
)

V1_API_URL_PREFIX = "api/v1/chat"

app_name = "chat"

router = AppSimpleRouter()
router.register(f"{V1_API_URL_PREFIX}/users/list", UserListAPIView)
router.register(f"{V1_API_URL_PREFIX}/user/onboard", UserOnboardAPIViewSet)
router.register(f"{V1_API_URL_PREFIX}/courses/list", CourseListAPIView)

urlpatterns = [
    path(f"{V1_API_URL_PREFIX}/course/cud/", CourseCUDApiView.as_view(), name="course_cud"),
    path(f"{V1_API_URL_PREFIX}/course/enroll/", CourseEnrollApiView.as_view(), name="course_enroll"),
    path(f"{V1_API_URL_PREFIX}/course/expert/onboard/", CourseExpertApiView.as_view(), name="course_expert"),
] + router.urls
