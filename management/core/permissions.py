"""
Logic to manage User role and authentication

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class CanEditOwnOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj or request.user.is_admin()
