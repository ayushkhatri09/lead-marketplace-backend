from rest_framework.permissions import BasePermission


class IsProviderAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return request.user is not None