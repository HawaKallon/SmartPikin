from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import View


class UserIsTeacherMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "teacher":
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UserIsAdmin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "admin":
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UserIsGuardianMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "guardian":
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UserIsOrganizerOrAdminMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["organizer", "admin"]:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
