from rest_framework.permissions import BasePermission

class isManager(BasePermission):
    
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="Manager").exists()